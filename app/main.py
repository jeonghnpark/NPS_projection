from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import matplotlib.pyplot as plt
import io
import base64
from pathlib import Path

from NPS_model import NationalPensionModel

app = FastAPI()


app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/calculate")
async def calculate(
    contribution_rate: float = Form(...), income_replacement: float = Form(...)
):
    try:
        model = NationalPensionModel()
        model.finance.params["contribution_rate"] = (
            contribution_rate / 100
        )  # 퍼센트를 비율로 변환
        model.benefit.params["income_replacement"] = income_replacement / 100
        results = model.run_projection()
        financial_results = results["financial_results"]

        plt.figure(figsize=(10, 6))
        years = [r["year"] for r in financial_results]
        reserve_funds = [
            r["nominal_reserve_fund"] / 100000000 for r in financial_results
        ]  # 조원 단위로 변환

        # 최대 적립금 시점 찾기
        max_reserve_idx = reserve_funds.index(max(reserve_funds))
        max_reserve_year = years[max_reserve_idx]
        max_reserve = reserve_funds[max_reserve_idx]

        # 적자전환 시점 찾기 (전년대비 감소 시작점)
        deficit_idx = next(
            i
            for i in range(1, len(reserve_funds))
            if reserve_funds[i] < reserve_funds[i - 1]
        )
        deficit_year = years[deficit_idx]

        # 기금 고갈 시점 찾기
        depletion_idx = next(
            (i for i, x in enumerate(reserve_funds) if x <= 0), len(years) - 1
        )
        depletion_year = years[depletion_idx]

        plt.plot(years, reserve_funds, marker="o")

        # 최대 적립금 표시
        plt.annotate(
            f"최대 적립금\n{max_reserve_year}년\n{max_reserve:.1f}조원",
            xy=(max_reserve_year, max_reserve),
            xytext=(10, 30),
            textcoords="offset points",
            ha="left",
            va="bottom",
            bbox=dict(boxstyle="round,pad=0.5", fc="yellow", alpha=0.5),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
        )

        # 적자전환 시점 표시
        plt.annotate(
            f"적자전환\n{deficit_year}년",
            xy=(deficit_year, reserve_funds[deficit_idx]),
            xytext=(-10, -30),
            textcoords="offset points",
            ha="right",
            va="top",
            bbox=dict(boxstyle="round,pad=0.5", fc="orange", alpha=0.5),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
        )

        # 기금 고갈 시점 표시
        plt.annotate(
            f"기금고갈\n{depletion_year}년",
            xy=(depletion_year, 0),
            xytext=(10, -30),
            textcoords="offset points",
            ha="left",
            va="top",
            bbox=dict(boxstyle="round,pad=0.5", fc="red", alpha=0.5),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
        )

        plt.title("연도별 적립금 추이")
        plt.xlabel("연도")
        plt.ylabel("적립금 (조원)")
        plt.grid(True)

        # 이미지를 바이트로 변환
        img_buf = io.BytesIO()
        plt.savefig(img_buf, format="png", bbox_inches="tight")
        plt.close()
        img_buf.seek(0)
        img_base64 = base64.b64encode(img_buf.getvalue()).decode()

        return JSONResponse(
            {
                "success": True,
                "image": img_base64,
                "max_reserve": max(reserve_funds),
                "depletion_year": years[
                    next(
                        (i for i, x in enumerate(reserve_funds) if x <= 0),
                        len(years) - 1,
                    )
                ],
            }
        )

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})
