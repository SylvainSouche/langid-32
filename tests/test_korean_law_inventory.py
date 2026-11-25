from langid32.korean_law_inventory import parse_law_body, parse_law_list


def test_parse_current_law_list():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <LawSearch>
      <totalCnt>1</totalCnt>
      <law>
        <법령일련번호>12345</법령일련번호>
        <법령명한글>테스트법</법령명한글>
        <법령약칭명>테스트</법령약칭명>
        <공포일자>20260101</공포일자>
        <시행일자>20260201</시행일자>
        <법령구분명>법률</법령구분명>
        <소관부처명>법제처</소관부처명>
        <법령상세링크>https://example.invalid/law</법령상세링크>
      </law>
    </LawSearch>""".encode("utf-8")
    total, records = parse_law_list(xml)
    assert total == 1
    assert records[0]["law_id"] == "12345"
    assert records[0]["group_id"] == "KR-LAW:12345"
    assert records[0]["source_licence"].startswith("Korean Copyright Act Article 7")
    assert records[0]["law_name"] == "테스트법"
    assert records[0]["effective_date"] == "20260201"


def test_parse_law_body_counts_articles_and_text():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <법령>
      <조문>
        <조문단위>
          <조문번호>1</조문번호>
          <조문제목>목적</조문제목>
          <조문내용>이 법은 목적을 정한다. 다음 사항을 규정한다.</조문내용>
        </조문단위>
        <조문단위>
          <조문번호>2</조문번호>
          <조문제목>정의</조문제목>
          <조문내용>용어의 뜻은 다음과 같다.</조문내용>
        </조문단위>
      </조문>
    </법령>""".encode("utf-8")
    result = parse_law_body(xml)
    assert result["article_count"] == 2
    assert result["rough_sentence_count"] == 3
    assert result["article_text_chars"] > 0
    assert len(result["body_sha256"]) == 64
