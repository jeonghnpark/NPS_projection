from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

now = datetime.now()
timestamp = now.strftime("%d%H%M")


def save_results_to_csv(rs):
    financial_df = pd.DataFrame(rs["financial_results"])
    demographic_df = pd.DataFrame(rs["demographic_results"])

    """결과 데이터프레임을 CSV 파일로 저장"""
    financial_df.to_csv(
        f"csv/financial_results_실질_{timestamp}.csv", encoding="utf-8-sig", index=False
    )
    demographic_df.to_csv(
        f"csv/demographic_results_실질_{timestamp}.csv",
        encoding="utf-8-sig",
        index=False,
    )


def create_financial_plots(rs):
    """재정추계 결과 시각화"""
    financial_df = pd.DataFrame(rs["financial_results"])

    # 1. 적립금 추이
    plt.figure(figsize=(10, 8))
    plt.plot(financial_df["year"], financial_df["reserve_fund"] / 100000000, marker="o")
    plt.title("연도별 적립금 추이", fontsize=12)
    plt.xlim(2023, 2085)
    plt.xlabel("연도", fontsize=10)
    plt.ylabel("적립금 (조원)", fontsize=10)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(
        f"images/nps_reserve_fund_{timestamp}.png", dpi=300, bbox_inches="tight"
    )
    plt.close()

    # 2. 수입-지출 추이
    plt.figure(figsize=(10, 8))
    plt.plot(
        financial_df["year"],
        financial_df["total_revenue"] / 100000000,
        marker="o",
        label="총수입",
    )
    plt.plot(
        financial_df["year"],
        financial_df["total_expenditure"] / 100000000,
        marker="o",
        label="총지출",
    )
    plt.title("연도별 수입-지출 추이", fontsize=12)
    plt.xlim(2023, 2085)
    plt.xlabel("연도", fontsize=10)
    plt.ylabel("금액 (조원)", fontsize=10)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(
        f"images/nps_revenue_expenditure_{timestamp}.png", dpi=300, bbox_inches="tight"
    )
    plt.close()

    # 3. 수지차 추이
    plt.figure(figsize=(10, 8))
    plt.plot(
        financial_df["year"],
        financial_df["balance"] / 100000000,
        marker="o",
        color="green",
    )
    plt.title("연도별 수지차 추이", fontsize=12)
    plt.xlim(2023, 2085)
    plt.xlabel("연도", fontsize=10)
    plt.ylabel("금액 (조원)", fontsize=10)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"images/nps_balance_{timestamp}.png", dpi=300, bbox_inches="tight")
    plt.close()

    # 4. 적립률 추이
    plt.figure(figsize=(10, 8))
    plt.plot(
        financial_df["year"], financial_df["fund_ratio"], marker="o", color="purple"
    )
    plt.title("연도별 적립률 추이", fontsize=12)
    plt.xlim(2023, 2085)
    plt.xlabel("연도", fontsize=10)
    plt.ylabel("적립률 (%)", fontsize=10)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"images/nps_fund_ratio_{timestamp}.png", dpi=300, bbox_inches="tight")
    plt.close()


def create_demographic_plots(rs):
    """인구 관련 지표 시각화"""
    demographic_df = pd.DataFrame(rs["demographic_results"])
    # 인구 관련 지표 4개 그래프를 2x2로 배치
    fig, axes = plt.subplots(2, 2, figsize=(20, 16))

    # 1. 인구 구조 추이 (좌상단)
    axes[0, 0].plot(
        demographic_df["year"],
        demographic_df["total_population"] / 10000,
        marker="o",
        label="총인구",
    )
    axes[0, 0].plot(
        demographic_df["year"],
        demographic_df["working_age_population"] / 10000,
        marker="o",
        label="생산가능인구",
    )
    axes[0, 0].plot(
        demographic_df["year"],
        demographic_df["elderly_population"] / 10000,
        marker="o",
        label="노인인구",
    )
    axes[0, 0].set_title("연도별 인구구조 추이", fontsize=12)
    axes[0, 0].set_xlim(2023, 2085)
    axes[0, 0].set_xlabel("연도", fontsize=10)
    axes[0, 0].set_ylabel("인구 (만명)", fontsize=10)
    axes[0, 0].legend()
    axes[0, 0].grid(True)

    # 2. 노년부양비 추이 (우상단)
    axes[0, 1].plot(
        demographic_df["year"],
        demographic_df["elderly_dependency"],
        marker="o",
        color="red",
    )
    axes[0, 1].set_title("연도별 노년부양비 추이", fontsize=12)
    axes[0, 1].set_xlim(2023, 2085)
    axes[0, 1].set_xlabel("연도", fontsize=10)
    axes[0, 1].set_ylabel("노년부양비 (%)", fontsize=10)
    axes[0, 1].grid(True)

    # 3. 가입자 수 추이 (좌하단)
    axes[1, 0].plot(
        demographic_df["year"],
        demographic_df["total_subscribers"] / 10000,
        marker="o",
        color="green",
    )
    axes[1, 0].set_title("연도별 가입자 수 추이", fontsize=12)
    axes[1, 0].set_xlim(2023, 2085)
    axes[1, 0].set_xlabel("연도", fontsize=10)
    axes[1, 0].set_ylabel("가입자 수 (만명)", fontsize=10)
    axes[1, 0].grid(True)

    # 4. 가입자 소득 추이 (우하단)
    axes[1, 1].plot(
        demographic_df["year"],
        demographic_df["total_income_nominal"] / 1_000_000_000,
        marker="o",
        label="명목소득",
    )
    axes[1, 1].plot(
        demographic_df["year"],
        demographic_df["total_income_real"] / 1_000_000_000,
        marker="o",
        label="실질소득",
    )
    axes[1, 1].set_title("연도별 가입자 소득 추이", fontsize=12)
    axes[1, 1].set_xlabel("연도", fontsize=10)
    axes[1, 1].set_xlim(2023, 2085)
    axes[1, 1].set_ylabel("총소득 (조원)", fontsize=10)
    axes[1, 1].legend()
    axes[1, 1].grid(True)

    plt.tight_layout()
    plt.savefig(
        f"images/nps_demographic_indicators_{timestamp}.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()
