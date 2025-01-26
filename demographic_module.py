import pandas as pd
import numpy as np


class DemographicModule:
    def __init__(self):
        """인구모듈 초기화"""

        # self.population_structure = None  # 전체 인구
        # 보고서 참조
        self.population_structure = create_initial_population_2023()

        self.working_age = None  # 생산가능인구 (18-64세)
        self.elderly = None  # 고령인구 (65세 이상)

        # 인구 변동요인 초기화 (중위가정 기준)
        self.params = {
            "fertility_rate": {  # 합계출산율
                2023: 0.73,
                2030: 0.96,
                2040: 1.19,
                2050: 1.21,
                2060: 1.21,
                2070: 1.21,
            },
            "life_expectancy": {  # 기대수명
                2023: 84.3,
                2030: 85.7,
                2040: 87.4,
                2050: 88.9,
                2060: 90.1,
                2070: 91.2,
            },
            "net_migration": {  # 국제순이동(천명) #TODO x1000반영확인 -> 천명단위로
                2023: 43,
                2030: 46,
                2040: 46,
                2050: 43,
                2060: 43,
                2070: 40,
            },
        }

    def load_initial_population(self, population_data_path):
        """초기 인구 데이터 로드
        함수 활용안되고 있음
        """
        # 연령별/성별 인구 구조 데이터 로드
        # self.population_structure = pd.read_csv(population_data_path)
        pass

    def project_population(self, year):
        """특정 연도의 인구추계"""
        # 1. 연령별/성별 인구구조 계산
        population_structure = self._calculate_population_structure(year)

        # 2. 주요 인구지표 계산
        demographic_indicators = {
            "year": year,
            "total_population": population_structure["total"].sum(),
            "working_age_population": population_structure[
                (population_structure["age"] >= 18) & (population_structure["age"] < 65)
            ]["total"].sum(),
            "elderly_population": population_structure[
                population_structure["age"] >= 65
            ]["total"].sum(),
        }
        demographic_indicators["elderly_dependency"] = (
            demographic_indicators["elderly_population"]
            / demographic_indicators["working_age_population"]
            * 100
        )

        return {
            "population_structure": population_structure,
            "indicators": demographic_indicators,
        }

    def _calculate_population_structure(self, year):
        """연령별/성별 인구구조 계산 (간단한 코호트 요인법)

        TODO :  더 정교한 연령별/성별 사망률 적용
            연령별 출산율 차등 적용
            연령별/성별 국제순이동 패턴 반영
            코호트별 특성 반영
        """
        if year == 2023:  # 기준연도는 초기 인구구조 반환
            return self.population_structure

        # 이전 연도의 인구구조로부터 계산
        prev_population_struct = self._calculate_population_structure(year - 1).copy()

        # 1. 연령 증가 (모든 연령층을 1세 증가)
        prev_population_struct["age"] += 1

        # 2. 사망률 적용 (간단한 연령별 사망률)
        survival_rates = self._get_survival_rates(prev_population_struct["age"])
        prev_population_struct["male"] *= survival_rates
        prev_population_struct["female"] *= survival_rates

        # 3. 출생아 수 계산
        fertility_rate = self.get_fertility_rate(year)
        fertile_women = prev_population_struct[
            (prev_population_struct["age"] >= 15)
            & (prev_population_struct["age"] <= 49)
        ]["female"].sum()

        total_births = (
            fertile_women * fertility_rate / (49 - 15 + 1)
        )  # 합계출산율->연간 출생아수로 전환

        # 출생성비 적용
        male_births = total_births * 0.5
        female_births = total_births * 0.5

        # 4. 신생아 행 추가
        newborn_row = pd.DataFrame(
            {
                "age": [0],
                "male": [male_births],
                "female": [female_births],
                "total": [male_births + female_births],
            }
        )

        # 5. 국제순이동 반영 (간단히 전체 인구에 비례하여 배분)
        net_migration = self._get_net_migration(year)
        migration_ratio = net_migration / prev_population_struct["total"].sum()

        prev_population_struct["male"] *= 1 + migration_ratio
        prev_population_struct["female"] *= 1 + migration_ratio

        # 6. 최종 인구구조 생성
        population_structure = pd.concat(
            [newborn_row, prev_population_struct[prev_population_struct["age"] <= 100]]
        )
        population_structure["total"] = (
            population_structure["male"] + population_structure["female"]
        )

        return population_structure.reset_index(drop=True)

    def _get_survival_rates(self, ages):
        """간단한 연령별 생존률 계산"""
        # 연령별 사망률 (매우 단순화된 버전)
        # 0세: 0.995, 1-39세: 0.999, 40-69세: 0.995, 70-89세: 0.98, 90세 이상: 0.90
        survival_rates = np.ones(len(ages))

        survival_rates[ages == 0] = 0.995
        survival_rates[(ages >= 1) & (ages < 40)] = 0.999
        survival_rates[(ages >= 40) & (ages < 70)] = 0.995
        survival_rates[(ages >= 70) & (ages < 90)] = 0.98
        survival_rates[ages >= 90] = 0.90

        return survival_rates

    def _get_net_migration(self, year):
        """특정 연도의 국제순이동자 수 반환"""
        years = sorted(self.params["net_migration"].keys())
        migration = [self.params["net_migration"][y] for y in years]

        return np.interp(year, years, migration) * 1000  # 천명 단위를 명 단위로 변환

    def get_fertility_rate(self, year):
        """특정 연도의 합계출산율 반환"""
        # 중간값은 선형보간
        years = sorted(self.params["fertility_rate"].keys())
        rates = [self.params["fertility_rate"][y] for y in years]

        return np.interp(year, years, rates)


def create_initial_population_2023():
    """2023년 초기 인구구조 생성
    국민연금 재정추계 자료 14페이지 참조

    """
    # 연령대별 인구 (만명)
    age_groups = {"under_18": 705, "18_64": 3501, "65_plus": 950}

    # 연령별 인구 분포 (더 세분화된 데이터가 필요)
    population_structure = []

    # 0-17세 인구 분포
    young_pop_per_age = age_groups["under_18"] * 10000 / 18  # 만명을 명으로 변환
    for age in range(18):
        population_structure.append(
            {
                "age": age,
                "total": young_pop_per_age,
                "male": young_pop_per_age * 0.515,  # 성비 가정
                "female": young_pop_per_age * 0.485,
            }
        )

    # 18-64세 인구 분포
    working_pop_per_age = age_groups["18_64"] * 10000 / 47
    for age in range(18, 65):
        population_structure.append(
            {
                "age": age,
                "total": working_pop_per_age,
                "male": working_pop_per_age * 0.505,
                "female": working_pop_per_age * 0.495,
            }
        )

    # 65세 이상 인구 분포
    elderly_pop_per_age = age_groups["65_plus"] * 10000 / 36  # 65-100세 가정
    for age in range(65, 101):
        population_structure.append(
            {
                "age": age,
                "total": elderly_pop_per_age,
                "male": elderly_pop_per_age * 0.45,  # 고령층 성비 반영
                "female": elderly_pop_per_age * 0.55,
            }
        )

    return pd.DataFrame(population_structure)


# 사용 예시
def test_demographic_module():
    demo = DemographicModule()

    # 가상의 초기 인구 데이터 생성
    # np.random.seed(42)
    # initial_population = pd.DataFrame(
    #     {
    #         "age": range(101),
    #         "male": np.random.normal(300000, 50000, 101),
    #         "female": np.random.normal(300000, 50000, 101),
    #         "total": np.random.normal(600000, 100000, 101),
    #     }
    # )

    # 5차 재정추계결과.pdf 자료로 초기 인구 데이터 생성

    demo.population_structure = create_initial_population_2023()

    # 2023년 인구추계 테스트
    # result_2023 = demo.project_population(2023)
    # print(f"2023년 추계결과:")
    # print(f"총인구: {result_2023['total_population']:,.0f}")
    # print(f"생산가능인구: {result_2023['working_age_population']:,.0f}")
    # print(f"고령인구: {result_2023['elderly_population']:,.0f}")
    # print(f"노년부양비: {result_2023['elderly_dependency']:.1f}%")

    # 2023년부터 2093년까지 인구추계 테스트
    results_list = []
    for year in range(2023, 2094):
        result = demo.project_population(year)
        results_list.append(
            {
                "year": year,
                "total_population": result["indicators"]["total_population"],
                "working_age_population": result["indicators"][
                    "working_age_population"
                ],
                "elderly_population": result["indicators"]["elderly_population"],
                "elderly_dependency": result["indicators"]["elderly_dependency"],
                "population_structure": result[
                    "population_structure"
                ],  # 인구구조 데이터 추가
            }
        )

    results_df = pd.DataFrame(results_list)
    print("\n인구추계 결과:")
    print(results_df)

    import matplotlib.pyplot as plt

    plt.figure(figsize=(12, 6))
    plt.plot(
        results_df["year"], results_df["total_population"] / 10000, "b-", linewidth=2
    )
    plt.title("total population(2023-2093)", fontsize=14)
    plt.xlabel("year", fontsize=12)
    plt.ylabel("total pupulation (10000 person)", fontsize=12)
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    test_demographic_module()
