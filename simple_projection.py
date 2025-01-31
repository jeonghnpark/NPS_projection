# 국민연금 재정추계 모델 (교육용 간소화 버전)
import pandas as pd

# ---------------------------
# 1. 기본 가정 변수 설정 (보고서 참조 부분 주석 처리)
# ---------------------------

# [인구 변수 - 보고서 참고1 (p15)]
total_fertility_rate = 0.73  # 2023년 합계출산율 (중위가정)
life_expectancy = 84.3  # 2023년 기대수명 (중위가정)
net_migration = 43000  # 2023년 국제순이동 (중위가정)

# [경제 변수 - 보고서 p16]
gdp_growth = 0.019  # 2023~2030년 실질경제성장률 (연평균 1.9%)
wage_growth = 0.019  # 2023~2030년 실질임금상승률 (연평균 1.9%)
inflation = 0.022  # 2023년 물가상승률 2.2%

# [기금 운용 - 보고서 p17]
fund_return = 0.045  # 기간평균 기금투자수익률 4.5%

# [추가 변수 - 통계청 및 지표누리에서 수집]
labor_participation = 62.5  # 2023년 경제활동참가율 (%) - 지표누리 2023년 12월
pension_coverage = 92.6  # 2023년 국민연금 가입률 (%) - 통계청 사회보장통계
avg_income = 35000000  # 2023년 평균소득 (원) - 통계청 가계동향조사

# ---------------------------
# 2. 초기값 설정 (2023년 기준)
# ---------------------------
years = 70  # 추계기간 2023~2093년
current_year = 2023
population = 51_560_000  # 2023년 총인구 (p18)
workers = 21_990_000  # 2023년 가입자 수 (p19)
pensioners = 5_270_000  # 2023년 수급자 수 (p19)
fund_balance = 915_000_000_000_000  # 기금잔고 ()

# ---------------------------
# 3. 재정추계 모델링 (단순화된 선형 예측)
# ---------------------------
results = []

for year in range(years):
    # 보험료 수입 계산 (가입자 * 평균소득 * 보험료율 9%)
    premium_income = workers * avg_income * 0.09

    # 급여 지출 계산 (수급자 * 평균급여)
    # (평균급여 = 평균소득 * 소득대체율 45% 가정)
    avg_pension = avg_income * 0.45
    benefit_payment = pensioners * avg_pension

    # 기금 수익 계산
    fund_income = fund_balance * fund_return

    # 재정수지 계산
    net_balance = premium_income + fund_income - benefit_payment
    fund_balance += net_balance

    # 결과 저장
    results.append(
        {
            "year": current_year + year,
            "workers": round(workers),
            "pensioners": round(pensioners),
            "avg_pension": round(avg_pension),
            "fund_income": round(fund_income),
            "premium_income": round(premium_income),
            "benefit_payment": round(benefit_payment),
            "fund_balance": round(fund_balance),
            "net_balance": round(net_balance),
        }
    )

    # 인구 감소 반영 (매년 0.5% 선형 감소 가정 - 보고서 p18 참조)
    population *= 0.995
    workers = population * (labor_participation / 100) * (pension_coverage / 100)
    pensioners = population * 0.184  # 65세 이상 인구 비율 18.4% (p18)

    # 소득 증가 반영
    avg_income *= 1 + wage_growth

# ---------------------------
# 4. 결과 출력
# ---------------------------
df = pd.DataFrame(results)
print("\n[재정추계 결과 요약]")
print(
    f"최대 기금잔고: {df['fund_balance'].max():,}원 ({df['year'][df['fund_balance'].idxmax()]}년)"
)
print(
    f"기금 소진 예상 연도: {df[df['fund_balance']<0]['year'].min() if any(df['fund_balance']<0) else 'N/A'}"
)
print(df)
# CSV 파일로 저장
df.to_csv("nps_projection_results.csv", index=False, encoding="utf-8-sig")
print("\nCSV 파일로 저장되었습니다: nps_projection_results.csv")

# ---------------------------
# 주요 가정 설명:
# 1. 인구 감소율: 보고서 p18의 전체인구 감소 추세 반영
# 2. 경제성장률: 보고서 p16의 중위가정 사용
# 3. 기금수익률: 보고서 p17의 4.5% 적용
# 4. 추가 데이터: 경제활동참가율, 평균소득 등 외부자료 활용
# 5. 단순화: 복잡한 인구 피라미드 대신 선형 감소 가정
# ---------------------------
