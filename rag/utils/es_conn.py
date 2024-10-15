import typing as t

from elastic_transport import ObjectApiResponse
from elasticsearch import AsyncElasticsearch

from rag.llm.embedding_model import EMBEDDING_MODEL
from rag.llm.rerank_model import RERANK_MODEL
import settings


class ESConnector:
    _host: str
    _username: str
    _password: str
    es_client: AsyncElasticsearch

    def __init__(self):
        self._host = settings.ELASTICSEARCH_HOST
        self._username = settings.ELASTICSEARCH_USERNAME
        self._password = settings.ELASTICSEARCH_PASSWORD

    async def connection(self) -> bool:
        self.es_client = AsyncElasticsearch(
            hosts=self._host,
            basic_auth=(self._username, self._password),
        )

        return await self._check_connection()

    async def _check_connection(self) -> bool:
        if not await self.es_client.ping():
            raise ConnectionError('ElasticDB connection failed')

        return True

    async def close_connection(self) -> None:
        await self.es_client.close()

    async def create_index(self, index_name: str) -> ObjectApiResponse[t.Any]:
        mappings = {
            "properties": {
                "doc_id": {
                    "type": "keyword",
                },
                "chunk_index": {
                    "type": "integer",
                    "index": False,
                },
                "title": {
                    "type": "text"
                },
                "content": {
                    "type": "text"
                },
                "vector": {
                    "type": "dense_vector",
                }
            }
        }

        return await self.es_client.indices.create(index=index_name, mappings=mappings)

    async def delete_index(self, index_name: str) -> ObjectApiResponse[t.Any]:
        return await self.es_client.indices.delete(index=index_name)

    async def delete_index_chunks(self, index_name: str, doc_id: str) -> ObjectApiResponse[t.Any]:
        # TODO: refactor size

        delete_query = {
            "query": {
                "bool": {
                    "filter": {
                        "term": {
                            "doc_id": doc_id
                        }
                    }
                }
            },
        }

        return await self.es_client.delete_by_query(index=index_name, body=delete_query)

    async def upsert_to_index(self, index_name: str, doc_id: str, title: str, chunks: list[str]) -> bool:

        try:
            if not self.es_client.indices.exists(index=index_name):
                raise KeyError(f'Index {index_name} does not exist')

            # TODO: check correct delete
            await self.delete_index_chunks(index_name=index_name, doc_id=doc_id)

            for inx, chunk in enumerate(chunks):
                vector = EMBEDDING_MODEL.encode(chunk)

                body = {
                    "doc_id": doc_id,
                    "chunk_index": inx + 1,
                    "title": title,
                    "content": chunk,
                    "vector": vector
                }

                await self.es_client.index(index=index_name, body=body)
        except Exception as e:
            raise e

        return True

    async def get_all_document_chunks(self,
                                      index_name: str,
                                      doc_id: str,
                                      page: int = 1,
                                      page_size: int = 10) -> list[dict]:

        from_value = (page - 1) * page_size

        body = {
            "_source": {
                "excludes": ["vector"]
            },
            "query": {
                "bool": {
                    "filter": {
                        "term": {
                            "doc_id": doc_id
                        }
                    }
                }
            },
            "from": from_value,
            "size": page_size
        }

        result = await self.es_client.search(index=index_name, body=body)

        return self._extract_results(result)

    async def hybrid_search(self, index_name: str, query: str, user_rerank: bool = True, threshold: float = 0.9,
                            k: int = 10) -> list[dict]:

        vector = EMBEDDING_MODEL.encode(query)

        body = {
            "_source": {
                "excludes": ["vector"]
            },
            "size": k,
            "query": {
                "function_score": {
                    "query": {
                        "bool": {
                            "should": [
                                {
                                    "match": {
                                        "content": {
                                            "query": query,
                                        }
                                    }
                                },
                                {
                                    "match": {
                                        "title": {
                                            "query": query,
                                            "boost": 1.5
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "functions": [
                        {
                            "script_score": {
                                "script": {
                                    "source": "cosineSimilarity(params.query_vector, 'vector')",
                                    "params": {
                                        "query_vector": vector,
                                        "weight": 4.0
                                    }
                                },

                            }
                        }
                    ],
                    "boost_mode": "multiply",
                    "score_mode": "multiply"
                }
            }
        }

        result = await self.es_client.search(index=index_name, body=body)

        extract_results = self._extract_results(result)
        if len(extract_results) == 0:
            return []

        if user_rerank:
            texts = [result['source']['content'] for result in extract_results]

            rerank_results = RERANK_MODEL.similarity(query=query, texts=texts)

            formatted_results = []
            for original, rerank in zip(extract_results, rerank_results):
                content, score = rerank
                if score >= threshold:
                    formatted_results.append({
                        "id": original["id"],
                        "score": score,
                        "index": original["index"],
                        "source": {
                            "doc_id": original["source"].get("doc_id", ""),
                            "chunk_index": original["source"].get("chunk_index", 0),
                            "title": original["source"].get("title", ""),
                            "content": content
                        }
                    })

            return formatted_results

        normalized_results = self._normalize_scores(extract_results)
        filtered_results = [res for res in normalized_results if res['score'] >= threshold]

        return filtered_results

    @classmethod
    def _extract_results(cls, response: dict) -> list[dict]:
        hits = response.get('hits', {}).get('hits', [])
        results = []
        for hit in hits:
            results.append({
                "id": hit["_id"],
                "score": hit["_score"],
                "index": hit["_index"],
                "source": hit["_source"]
            })

        return results

    @classmethod
    def _normalize_scores(cls, results) -> list[dict]:

        if not all(isinstance(res, dict) for res in results):
            raise TypeError("Each item in results must be a dictionary")

        scores = [res['score'] for res in results if 'score' in res]

        if not scores:
            return []

        min_score = min(scores)
        max_score = max(scores)

        for res in results:
            if 'score' in res:
                score = res['score']
                if max_score != min_score:
                    normalized_score = (score - min_score) / (max_score - min_score)
                else:
                    normalized_score = 1.0

                res['score'] = normalized_score

        return results


ELASTICSEARCH = ESConnector()
