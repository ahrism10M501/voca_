# DBOpen에서 뽑은 데이터는 중복 단어 처리가 되어있지 않음.
# 각 뜻에 일대일대응 되어 있기 때문에 한 번 가공해줄 필요가 있음.
# 이를 처리하기 위한 함수

def VocaTransformer(data):
    data = [(word, meaning) for word_id, word, day, level, meaning_id, word_id2, meaning in data]
    voca = {}
    temp = []
    
    for word, mean in data:
        if word in voca.keys():
            voca[word].append(mean)
        else:
            voca[word] = [mean]

    for k, v in voca.items():
        temp.append((k, ", ".join(v)))

    return temp

if __name__ == "__main__":
            # word_id, word, day, level, meaning_id, word_id, meaning
    data = [(10, 'confidence', 1, 1, 26, 10, '~에 대한 확신'),
            (40, 'prospective', 1, 1, 71, 40, '미래의'),
            (10, 'confidence', 1, 1, 20, 10, '신임'),
            (10, 'confidence', 1, 1, 19, 10, '자신'),
            (40, 'prospective', 1, 1, 70, 40, '장래의'),
            (30, 'condition', 1, 1, 56, 30, '조건'),
            (20, 'reference', 1, 1, 38, 20, '참고'),
            (20, 'reference', 1, 1, 37, 20, '추천서'),
            (10, 'confidence', 1, 1, 18, 10, '확신')]
    
    print(VocaTransformer(data))