import re


class TxtParser:
    def __call__(self, text, chunk_size=512, overlap: int = 0, delimiter=r'\n|!|\?|;|。|；|！|？'):
        return self.parser_txt(text=text, chunk_size=chunk_size, overlap=overlap, delimiter=delimiter)

    @classmethod
    def parser_txt(cls, text, chunk_size=512, overlap=0, delimiter=r'\n|!|\?|;|。|；|！|？'):
        chunks = []
        current_position = 0
        text_length = len(text)

        delimiter_pattern = re.compile(delimiter)

        while current_position < text_length:
            next_position = min(current_position + chunk_size, text_length)

            match = delimiter_pattern.search(text, next_position)

            if match:
                next_position = match.end()

            chunks.append(text[current_position:next_position])

            current_position = next_position

            if overlap > 0 and len(chunks) > 1:
                previous_chunk = chunks[-2]
                overlap_chunk = previous_chunk[-overlap:]
                chunks[-1] = overlap_chunk + chunks[-1]

        return chunks
