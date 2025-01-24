from demographic_module import DemographicModule
from economic_module import EconomicModule
from finance_module import FinanceModule, SubscriberModule, BenefitModule
from datetime import datetime
import pandas as pd

from datetime import datetime

now = datetime.now()
timestamp = now.strftime("%d%H%M")


class NationalPensionModel:
    def __init__(self):
        self.start_year = 2023  # 고정해야함 초기값등
        self.end_year = 2093

        # 주요 모듈 초기화
        self.demographic = DemographicModule()  # 인구모듈
        self.economic = EconomicModule()  # 경제모듈
        self.subscriber = SubscriberModule()  # 가입자모듈
        self.benefit = BenefitModule()  # 급여모듈
        self.finance = FinanceModule()  # 재정모듈

    def run_projection(self):
        """재정추계 실행"""
        results = []
        demographic_results = []  # 인구지표 저장용

        for year in range(self.start_year, self.end_year + 1):
            # 1. 인구추계
            population_data = self.demographic.project_population(year)
            # demographic_results.append(population_data["indicators"])

            # 2. 거시경제변수 추계
            economic_vars = self.economic.project_variables(year)

            # 3. 가입자 추계
            subscribers = self.subscriber.project_subscribers(
                year, population_data["population_structure"]
            )

            # 인구지표와 가입자 정보를 통합
            demographic_data = population_data["indicators"].copy()
            demographic_data.update(
                {
                    "total_subscribers": subscribers["total_subscribers"],
                    "total_income_nominal": subscribers["total_income_nominal"],
                    "total_income_real": subscribers["total_income_real"],
                }
            )

            demographic_results.append(demographic_data)

            # 4. 급여지출 추계
            benefits = self.benefit.project_benefits(
                year,
                population_data["population_structure"],  # 인구구조 데이터 추가
                subscribers,
            )

            # 5. 재정수지 추계
            financial_status = self.finance.project_balance(
                year, subscribers, benefits, economic_vars
            )

            # print(financial_status)
            results.append(financial_status)

        return {
            "financial_results": results,
            "demographic_results": demographic_results,
        }


nps = NationalPensionModel()
rs = nps.run_projection()


financial_df = pd.DataFrame(rs["financial_results"])
demographic_df = pd.DataFrame(rs["demographic_results"])

financial_df.to_csv(
    f"financial_results_실질_{timestamp}.csv", encoding="utf-8-sig", index=False
)
demographic_df.to_csv(
    f"demographic_results_실질_{timestamp}.csv", encoding="utf-8-sig", index=False
)

print(f"재정추계 결과가 financial_results_실질_{timestamp}.csv로 저장되었습니다.")
print(f"인구추계 결과가 demographic_results_실질_{timestamp}.csv로 저장되었습니다.")
