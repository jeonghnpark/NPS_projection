# 재정모듈
import pandas as pd
import numpy as np


class FinanceModule:
    def __init__(self):
        self.params = {
            "contribution_rate": 0.09,
            "nominal_investment_return": {
                2023: 0.049,
                2030: 0.049,
                2040: 0.046,
                2050: 0.045,
                2060: 0.045,
            },
            "inflation_rate": {
                2023: 0.022,
                2024: 0.022,
                2025: 0.022,
                2026: 0.022,
                2027: 0.022,
                2030: 0.022,
                2040: 0.020,
                2050: 0.020,
                2060: 0.020,
            },
            "real_investment_return": {
                2023: 0.025,
                2030: 0.022,
                2040: 0.020,
                2050: 0.020,
                2060: 0.020,
            },
        }

        self.reserve_fund = 915e8  # 2023년 초기 적립금 (915조원): 단위 만원
        self.real_reserve_fund = 915e8  # 2023년 초기 실질 적립금 (915조원): 단위 만원

    def project_balance(self, year, subscribers, benefits, economic_vars):
        """재정수지 추계"""
        # 1. 수입 추계
        total_revenue = self._calculate_total_revenue(year, subscribers, economic_vars)

        # 2. 지출 추계
        total_expenditure = self._calculate_total_expenditure(year, benefits)

        # 3. 수지차 계산
        balance = total_revenue - total_expenditure

        # 4. 적립금 계산 (실질가치에서 명목가치로 변환)
        cumulative_inflation = self._get_cumulative_inflation(2023, year)
        nominal_balance = balance * cumulative_inflation

        # 적립금은 명목가치로 관리
        self.reserve_fund = self._calculate_reserve_fund(year, nominal_balance)

        # 보고서 결과와 비교를 위해 실질가치로 변환
        real_reserve_fund = self.reserve_fund / cumulative_inflation

        return {
            "year": year,
            "total_revenue": total_revenue,
            "total_expenditure": total_expenditure,
            "balance": balance,
            "reserve_fund": real_reserve_fund,  # 실질 적립금
            "fund_ratio": self.reserve_fund / total_expenditure,  # 적립배율
        }

    def _get_cumulative_inflation(self, base_year, target_year):
        """기준연도 대비 목표연도까지의 누적 물가상승률 계산"""
        cumulative = 1.0
        for year in range(base_year + 1, target_year + 1):
            inflation_rate = self._get_inflation_rate(year)
            cumulative *= 1 + inflation_rate
        return cumulative

    def _calculate_total_revenue(self, year, subscribers, economic_vars):
        """총수입 계산 (실질가치 기준)"""
        # 1. 보험료 수입 (실질가치)
        contribution_revenue = (
            subscribers["total_income_real"] * self.params["contribution_rate"]
        )

        # 2. 투자 수익 (실질수익률 적용)
        real_return = self._get_real_investment_return(year)
        investment_revenue = self.reserve_fund * real_return

        return contribution_revenue + investment_revenue

    def _calculate_total_expenditure(self, year, benefits):
        """총지출 계산"""
        # 1. 연금급여 지출
        benefit_expenditure = benefits["total_benefits_real"]  # 실질가치 기준

        # 2. 관리운영비 (급여지출의 1% 가정)
        admin_cost = benefit_expenditure * 0.01

        return benefit_expenditure + admin_cost

    def _calculate_reserve_fund(self, year, balance):
        """적립금 계산"""
        # 전년도 적립금 + 당해연도 수지
        new_reserve_fund = self.reserve_fund + balance

        # 적립금이 음수가 되는 경우 0으로 처리
        return max(0, new_reserve_fund)

    def _get_real_investment_return(self, year):
        """특정 연도의 실질투자수익률 반환"""
        # 실질투자수익률 직접 사용
        years = sorted(self.params["real_investment_return"].keys())
        rates = [self.params["real_investment_return"][y] for y in years]

        # 주어진 연도들 사이의 값은 선형보간
        # 주어진 연도 이후는 마지막 값으로 유지
        if year >= years[-1]:
            return rates[-1]
        else:
            return np.interp(year, years, rates)

    def _get_nominal_investment_return(self, year):
        """특정 연도의 명목투자수익률 반환"""
        years = sorted(self.params["nominal_investment_return"].keys())
        rates = [self.params["nominal_investment_return"][y] for y in years]

        if year >= years[-1]:
            return rates[-1]
        else:
            return np.interp(year, years, rates)

    def _get_inflation_rate(self, year):
        """특정 연도의 물가상승률 반환"""
        years = sorted(self.params["inflation_rate"].keys())
        rates = [self.params["inflation_rate"][y] for y in years]

        if year >= years[-1]:
            return rates[-1]
        else:
            return np.interp(year, years, rates)


class SubscriberModule:
    def __init__(self):
        """가입자모듈 초기화"""
        self.params = {
            "participation_rate": {  # 가입률
                (18, 27): 0.50,  # 청년층
                (28, 49): 0.80,  # 핵심근로층
                (50, 59): 0.70,  # 준고령층
                (60, 64): 0.40,  # 고령층
            },
            "avg_income": {  # 연령대별 평균소득
                (18, 27): 250,  # 월 250만원
                (28, 49): 350,
                (50, 59): 380,
                (60, 64): 300,
            },
            "inflation_rate": {  # 물가상승률 (보고서 p.12 참조)
                2023: 0.022,
                2024: 0.022,
                2025: 0.022,
                2026: 0.022,
                2027: 0.022,
                2030: 0.022,
                2040: 0.020,
                2050: 0.020,
                2060: 0.020,
            },
        }

    def _get_inflation_rate(self, year):
        """물가상승률 반환 (FinanceModule의 메서드 활용)"""
        # FinanceModule의 inflation_rate 파라미터 사용
        years = sorted(self.params["inflation_rate"].keys())
        rates = [self.params["inflation_rate"][y] for y in years]

        if year >= years[-1]:
            return rates[-1]
        return np.interp(year, years, rates)

    def project_subscribers(self, year, population_structure):
        """가입자 추계"""
        subscribers = {}
        total_income_nominal = 0
        total_income_real = 0

        for age_group, rate in self.params["participation_rate"].items():
            # 해당 연령대 인구
            age_pop = population_structure[
                (population_structure["age"] >= age_group[0])
                & (population_structure["age"] <= age_group[1])
            ]["total"].sum()

            # 가입자 수 계산
            subscribers[age_group] = age_pop * rate

            # 소득 계산
            avg_income = self.params["avg_income"][age_group]
            total_income_nominal += subscribers[age_group] * avg_income * 12

            # 실질가치 변환을 위한 물가상승률 적용
            cumulative_inflation = 1.0
            base_year = 2023
            for y in range(base_year + 1, year + 1):
                inflation_rate = self._get_inflation_rate(y)
                cumulative_inflation *= 1 + inflation_rate

            total_income_real = total_income_nominal / cumulative_inflation

        return {
            "year": year,
            "subscribers": subscribers,
            "total_subscribers": sum(subscribers.values()),
            "total_income_nominal": total_income_nominal,
            "total_income_real": total_income_real,
        }


class BenefitModule:
    def __init__(self):
        """급여모듈 초기화"""
        self.params = {
            "income_replacement": 0.40,  # 소득대체율 40%
            "avg_insured_period": {  # 평균가입기간
                2023: 15,
                2030: 18,
                2040: 22,
                2050: 25,
                2060: 28,
            },
            "benefit_rate": {  # 수급률 (65세 이상 인구 대비)
                2023: 0.440,  # 44.0%
                2030: 0.550,
                2040: 0.650,
                2050: 0.750,
                2060: 0.800,
            },
            "inflation_rate": {  # 물가상승률 (보고서 p.12 참조)
                2023: 0.022,
                2024: 0.022,
                2025: 0.022,
                2026: 0.022,
                2027: 0.022,
                2030: 0.022,
                2040: 0.020,
                2050: 0.020,
                2060: 0.020,
            },
        }

    def _get_inflation_rate(self, year):  # subscriber와 중복됨 개선필요
        """특정 연도의 물가상승률 반환"""
        years = sorted(self.params["inflation_rate"].keys())
        rates = [self.params["inflation_rate"][y] for y in years]

        if year >= years[-1]:
            return rates[-1]
        return np.interp(year, years, rates)

    def _get_benefit_rate(self, year):
        """특정 연도의 수급률 반환"""
        years = sorted(self.params["benefit_rate"].keys())
        rates = [self.params["benefit_rate"][y] for y in years]

        if year >= years[-1]:
            return rates[-1]
        return np.interp(year, years, rates)

    def _get_avg_insured_period(self, year):
        """특정 연도의 평균가입기간 반환"""
        years = sorted(self.params["avg_insured_period"].keys())
        periods = [self.params["avg_insured_period"][y] for y in years]

        if year >= years[-1]:
            return periods[-1]
        return np.interp(year, years, periods)

    def project_benefits(self, year, population_structure, subscribers_data):
        """급여지출 추계"""
        # 1. 수급자 수 추계
        elderly_pop = population_structure[population_structure["age"] >= 65][
            "total"
        ].sum()
        benefit_rate = self._get_benefit_rate(year)
        beneficiaries = elderly_pop * benefit_rate

        # 2. 평균급여액 계산
        avg_insured_period = self._get_avg_insured_period(year)
        avg_income = (
            subscribers_data["total_income_nominal"]
            / subscribers_data["total_subscribers"]
        )
        avg_benefit = (
            avg_income
            * self.params["income_replacement"]
            * (avg_insured_period / 40)  # 40년 만기 기준
        )

        # 3. 총급여지출 계산
        total_benefits_nominal = beneficiaries * avg_benefit

        # 4. 실질가치 변환
        cumulative_inflation = 1.0
        base_year = 2023
        for y in range(base_year + 1, year + 1):
            inflation_rate = self._get_inflation_rate(y)
            cumulative_inflation *= 1 + inflation_rate

        total_benefits_real = total_benefits_nominal / cumulative_inflation

        return {
            "year": year,
            "beneficiaries": beneficiaries,
            "avg_benefit": avg_benefit,
            "total_benefits_nominal": total_benefits_nominal,
            "total_benefits_real": total_benefits_real,  # 실질가치로 변환된 총급여지출
        }
