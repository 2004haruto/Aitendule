from fastapi import APIRouter, HTTPException, Request
from datetime import date
from db import get_connection  # ← これを使う

router = APIRouter()

CATEGORY_NAME_MAP = {
    "トップス": "tops",
    "ボトムス": "bottoms",
    "靴": "shoes",
    "アウター": "outer",
    "小物": "accessory",
}

@router.post("/api/v1/save_choice")
async def save_choice(request: Request):
    try:
        body = await request.json()
        user_id = body.get("user_id")
        choice = body.get("choice", {})
        weather = body.get("weather")
        temperature = body.get("temperature")
        is_recommended = body.get("is_recommended", 0)

        if not user_id or not choice:
            raise HTTPException(status_code=400, detail="ユーザーIDと服装データは必須です")

        conn = get_connection()
        cursor = conn.cursor()

        for category_jp, item_name in choice.items():
            category_en = CATEGORY_NAME_MAP.get(category_jp, category_jp)

            # 服装アイテムが既にあるか確認
            cursor.execute("""
                SELECT clothing_id FROM clothing_items
                WHERE name = %s AND category = %s
            """, (item_name, category_en))
            result = cursor.fetchone()

            if result:
                clothing_id = result[0]
            else:
                # 新規登録
                cursor.execute("""
                    INSERT INTO clothing_items (name, category)
                    VALUES (%s, %s)
                """, (item_name, category_en))
                clothing_id = cursor.lastrowid

            # 選択記録を保存
            cursor.execute("""
                INSERT INTO user_clothing_choices (
                    user_id, clothing_id, choice_date, weather, temperature, is_recommended
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                clothing_id,
                date.today(),
                weather,
                temperature,
                is_recommended
            ))

        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "服装の選択を保存しました"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ サーバーエラー: {str(e)}")
