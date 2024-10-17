import spacy
from spacy.lang.ru.examples import sentences

keyword = ("Я не могу предоставить информацию о конкретной статье или законопроекте, включая текст статьи 60.1 Банка "
           "России.\n\nЕсли ключевые слова: Статья 60.1 Банк России/ \n вы хотите получить более общую информацию об "
           "этом вопросе, я могу помочь вам с этим. Например: \n\n")

nlp = spacy.load("en_core_web_md")

nlp.add_pipe("keyword_extractor", last=True, config={"top_n": 10, "min_ngram": 3, "max_ngram": 3, "strict": True})

doc = nlp(keyword)
print("Top Keywords:", doc._.keywords)

# doc = nlp(keyword)
#
# print(doc._.span_extensions)

# # print(doc.text)
# for token in doc:
#     print(t)


