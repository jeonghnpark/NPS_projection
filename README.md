# 국민연금 재정추계 모델

## 프로젝트 소개
이 프로젝트는 국민연금의 장기 재정추계를 수행하는 파이썬 기반 모델입니다. 2023년부터 2093년까지의 국민연금 재정상태를 예측합니다.

## 주요 기능
- 인구추계 (DemographicModule)
- 거시경제변수 추계 (EconomicModule)
- 가입자 추계 (SubscriberModule)
- 급여지출 추계 (BenefitModule)
- 재정수지 추계 (FinanceModule)

## 프로젝트 구조
- NPS_model.py # 메인 모델
- demographic_module.py # 인구 모듈
- economic_module.py # 경제 모듈
- finance_module.py # 재정/가입자/급여 모듈
- README.md

## 테스트 결과
![재정추계 결과](./financial_projection_241739.png)


테스트 결과는 위 그래프와 같습니다. 주요 결과는 다음과 같습니다:
- 적립금은 2040년대 초반 최고치 도달 후 감소
- 수지적자는 2040년대 초반부터 발생
- 적립배율은 2054년에 1배 미만으로 하락


## 설치 방법
bash
git clone [repository-url]
cd [project-directory]
pip install -r requirements.txt
## 사용 방법
python
from NPS_model import NationalPensionModel

## 모델 초기화
nps = NationalPensionModel()
## 추계 실행
results = nps.run_projection()


## 출력 결과
모델은 두 가지 CSV 파일을 생성합니다:
- `financial_results_실질_[timestamp].csv`: 재정추계 결과
- `demographic_results_실질_[timestamp].csv`: 인구추계 결과

## 주요 매개변수
### 인구 변수
- 합계출산율: 2023년 0.73명 → 2050년 1.21명
- 기대수명: 2023년 84.3세 → 2070년 91.2세
- 국제순이동: 연간 4-5만명 수준

### 경제 변수
- GDP 성장률: 2023년 2.2% → 2060년 0.7%
- 임금상승률: 2023년 2.3% → 2060년 1.5%
- 물가상승률: 2023년 3.3% → 2027년 이후 2.0%

### 연금 변수
- 보험료율: 9%
- 소득대체율: 40%
- 수급개시연령: 65세

## 기술 스택
- Python 3.x
- pandas
- numpy

## 시스템 요구사항
- Python 3.8 이상
- pandas 1.0.0 이상
- numpy 1.18.0 이상

## 라이선스
내부용

## 연락처
[담당자 정보 추가 필요]

## 참고문헌
- 국민연금 제5차 재정계산 결과 (2023)
