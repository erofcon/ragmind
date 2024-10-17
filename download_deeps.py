import os

from huggingface_hub import snapshot_download

repos = [
    'BAAI/bge-m3',
    'BAAI/bge-reranker-v2-m3'
]

spacy_models = [
    'ru_core_news_lg'
]


def download_model(repo_id: str):
    local_dir = os.path.abspath(os.path.join("huggingface", repo_id))
    os.makedirs(local_dir, exist_ok=True)
    snapshot_download(repo_id=repo_id, local_dir=local_dir)


if __name__ == "__main__":

    for repo_id in repos:
        print(f"Downloading huggingface repo {repo_id}...")
        download_model(repo_id)
