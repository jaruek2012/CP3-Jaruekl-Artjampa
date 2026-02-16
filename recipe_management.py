import json
import os

DATA_FILE = "recipe_data.json"


# ==================== ฟังก์ชันจัดการข้อมูล ====================

def load_data():
    """โหลดข้อมูลจากไฟล์ JSON"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"ingredients": [], "recipes": [], "production_log": []}


def save_data(data):
    """บันทึกข้อมูลลงไฟล์ JSON"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_next_id(items):
    """สร้าง ID ถัดไป"""
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


# ==================== จัดการวัตถุดิบ ====================

def add_ingredient(data):
    """เพิ่มวัตถุดิบใหม่"""
    print("\n===== เพิ่มวัตถุดิบ =====")
    name = input("ชื่อวัตถุดิบ: ").strip()
    if not name:
        print("❌ กรุณาระบุชื่อวัตถุดิบ")
        return

    unit = input("หน่วย (เช่น กก., กรัม, ลิตร, มล., ชิ้น): ").strip()
    if not unit:
        print("❌ กรุณาระบุหน่วย")
        return

    try:
        price = float(input("ราคาต่อหน่วย (บาท): "))
        stock = float(input("จำนวนในสต๊อค: "))
    except ValueError:
        print("❌ กรุณาระบุตัวเลขที่ถูกต้อง")
        return

    if price < 0 or stock < 0:
        print("❌ ราคาและจำนวนต้องไม่ติดลบ")
        return

    ingredient = {
        "id": get_next_id(data["ingredients"]),
        "name": name,
        "unit": unit,
        "price_per_unit": price,
        "stock": stock,
    }
    data["ingredients"].append(ingredient)
    save_data(data)
    print(f"✅ เพิ่มวัตถุดิบ '{name}' เรียบร้อย (ID: {ingredient['id']})")


def list_ingredients(data):
    """แสดงรายการวัตถุดิบทั้งหมด"""
    print("\n===== รายการวัตถุดิบ =====")
    if not data["ingredients"]:
        print("(ยังไม่มีวัตถุดิบ)")
        return

    print(f"{'ID':<5} {'ชื่อ':<20} {'หน่วย':<10} {'ราคา/หน่วย':>12} {'สต๊อค':>10}")
    print("-" * 60)
    for ing in data["ingredients"]:
        print(
            f"{ing['id']:<5} {ing['name']:<20} {ing['unit']:<10} "
            f"{ing['price_per_unit']:>10.2f}  {ing['stock']:>10.2f}"
        )


def edit_ingredient(data):
    """แก้ไขวัตถุดิบ"""
    list_ingredients(data)
    if not data["ingredients"]:
        return

    try:
        ing_id = int(input("\nระบุ ID วัตถุดิบที่ต้องการแก้ไข: "))
    except ValueError:
        print("❌ ID ไม่ถูกต้อง")
        return

    ingredient = next((i for i in data["ingredients"] if i["id"] == ing_id), None)
    if not ingredient:
        print("❌ ไม่พบวัตถุดิบ ID นี้")
        return

    print(f"\nกำลังแก้ไข: {ingredient['name']} (กด Enter เพื่อข้ามไม่แก้ไข)")

    name = input(f"  ชื่อ [{ingredient['name']}]: ").strip()
    unit = input(f"  หน่วย [{ingredient['unit']}]: ").strip()
    price = input(f"  ราคา/หน่วย [{ingredient['price_per_unit']}]: ").strip()
    stock = input(f"  สต๊อค [{ingredient['stock']}]: ").strip()

    if name:
        ingredient["name"] = name
    if unit:
        ingredient["unit"] = unit
    if price:
        try:
            ingredient["price_per_unit"] = float(price)
        except ValueError:
            print("❌ ราคาไม่ถูกต้อง ข้ามการแก้ไขราคา")
    if stock:
        try:
            ingredient["stock"] = float(stock)
        except ValueError:
            print("❌ จำนวนไม่ถูกต้อง ข้ามการแก้ไขสต๊อค")

    save_data(data)
    print("✅ แก้ไขวัตถุดิบเรียบร้อย")


def delete_ingredient(data):
    """ลบวัตถุดิบ"""
    list_ingredients(data)
    if not data["ingredients"]:
        return

    try:
        ing_id = int(input("\nระบุ ID วัตถุดิบที่ต้องการลบ: "))
    except ValueError:
        print("❌ ID ไม่ถูกต้อง")
        return

    ingredient = next((i for i in data["ingredients"] if i["id"] == ing_id), None)
    if not ingredient:
        print("❌ ไม่พบวัตถุดิบ ID นี้")
        return

    # ตรวจสอบว่ามีสูตรใช้วัตถุดิบนี้อยู่หรือไม่
    used_in = [
        r["name"]
        for r in data["recipes"]
        if any(item["ingredient_id"] == ing_id for item in r["ingredients"])
    ]
    if used_in:
        print(f"⚠️  วัตถุดิบนี้ถูกใช้ในสูตร: {', '.join(used_in)}")
        confirm = input("ต้องการลบต่อหรือไม่? (y/n): ").strip().lower()
        if confirm != "y":
            print("ยกเลิกการลบ")
            return

    data["ingredients"].remove(ingredient)
    save_data(data)
    print(f"✅ ลบวัตถุดิบ '{ingredient['name']}' เรียบร้อย")


def restock_ingredient(data):
    """เพิ่มสต๊อควัตถุดิบ"""
    list_ingredients(data)
    if not data["ingredients"]:
        return

    try:
        ing_id = int(input("\nระบุ ID วัตถุดิบที่ต้องการเพิ่มสต๊อค: "))
    except ValueError:
        print("❌ ID ไม่ถูกต้อง")
        return

    ingredient = next((i for i in data["ingredients"] if i["id"] == ing_id), None)
    if not ingredient:
        print("❌ ไม่พบวัตถุดิบ ID นี้")
        return

    try:
        qty = float(input(f"จำนวนที่ต้องการเพิ่ม ({ingredient['unit']}): "))
    except ValueError:
        print("❌ จำนวนไม่ถูกต้อง")
        return

    if qty <= 0:
        print("❌ จำนวนต้องมากกว่า 0")
        return

    ingredient["stock"] += qty
    save_data(data)
    print(
        f"✅ เพิ่มสต๊อค '{ingredient['name']}' จำนวน {qty} {ingredient['unit']} "
        f"(คงเหลือ: {ingredient['stock']} {ingredient['unit']})"
    )


# ==================== จัดการสูตรอาหาร ====================

def find_ingredient_by_id(data, ing_id):
    """ค้นหาวัตถุดิบจาก ID"""
    return next((i for i in data["ingredients"] if i["id"] == ing_id), None)


def add_recipe(data):
    """เพิ่มสูตรอาหารใหม่"""
    print("\n===== เพิ่มสูตรอาหาร =====")

    if not data["ingredients"]:
        print("❌ ยังไม่มีวัตถุดิบ กรุณาเพิ่มวัตถุดิบก่อน")
        return

    name = input("ชื่อสูตรอาหาร: ").strip()
    if not name:
        print("❌ กรุณาระบุชื่อสูตร")
        return

    try:
        servings = int(input("จำนวนที่ผลิตได้ต่อสูตร (เสิร์ฟ/ชิ้น): "))
    except ValueError:
        print("❌ จำนวนไม่ถูกต้อง")
        return

    if servings <= 0:
        print("❌ จำนวนต้องมากกว่า 0")
        return

    print("\n--- เลือกวัตถุดิบ ---")
    list_ingredients(data)

    recipe_ingredients = []
    while True:
        ing_input = input("\nระบุ ID วัตถุดิบ (หรือ Enter เพื่อเสร็จสิ้น): ").strip()
        if not ing_input:
            break

        try:
            ing_id = int(ing_input)
        except ValueError:
            print("❌ ID ไม่ถูกต้อง")
            continue

        ingredient = find_ingredient_by_id(data, ing_id)
        if not ingredient:
            print("❌ ไม่พบวัตถุดิบ ID นี้")
            continue

        # ตรวจสอบว่าเพิ่มซ้ำหรือไม่
        if any(ri["ingredient_id"] == ing_id for ri in recipe_ingredients):
            print("⚠️  วัตถุดิบนี้ถูกเพิ่มแล้ว")
            continue

        try:
            qty = float(
                input(
                    f"จำนวน '{ingredient['name']}' ที่ใช้ ({ingredient['unit']}): "
                )
            )
        except ValueError:
            print("❌ จำนวนไม่ถูกต้อง")
            continue

        if qty <= 0:
            print("❌ จำนวนต้องมากกว่า 0")
            continue

        recipe_ingredients.append({"ingredient_id": ing_id, "quantity": qty})
        print(f"  + {ingredient['name']} {qty} {ingredient['unit']}")

    if not recipe_ingredients:
        print("❌ สูตรต้องมีวัตถุดิบอย่างน้อย 1 รายการ")
        return

    recipe = {
        "id": get_next_id(data["recipes"]),
        "name": name,
        "servings": servings,
        "ingredients": recipe_ingredients,
    }
    data["recipes"].append(recipe)
    save_data(data)
    print(f"✅ เพิ่มสูตร '{name}' เรียบร้อย (ID: {recipe['id']})")


def list_recipes(data):
    """แสดงรายการสูตรอาหารทั้งหมด"""
    print("\n===== รายการสูตรอาหาร =====")
    if not data["recipes"]:
        print("(ยังไม่มีสูตรอาหาร)")
        return

    for recipe in data["recipes"]:
        cost = calculate_recipe_cost(data, recipe)
        print(f"\n[ID: {recipe['id']}] {recipe['name']} (ผลิตได้ {recipe['servings']} เสิร์ฟ/สูตร)")
        print(f"  ต้นทุนรวม: {cost:.2f} บาท | ต้นทุนต่อเสิร์ฟ: {cost / recipe['servings']:.2f} บาท")
        print("  วัตถุดิบ:")
        for item in recipe["ingredients"]:
            ing = find_ingredient_by_id(data, item["ingredient_id"])
            if ing:
                item_cost = item["quantity"] * ing["price_per_unit"]
                print(
                    f"    - {ing['name']}: {item['quantity']} {ing['unit']} "
                    f"(หน่วยละ {ing['price_per_unit']:.2f} = {item_cost:.2f} บาท)"
                )
            else:
                print(f"    - [วัตถุดิบ ID {item['ingredient_id']} ถูกลบแล้ว]")


def edit_recipe(data):
    """แก้ไขสูตรอาหาร"""
    list_recipes(data)
    if not data["recipes"]:
        return

    try:
        recipe_id = int(input("\nระบุ ID สูตรที่ต้องการแก้ไข: "))
    except ValueError:
        print("❌ ID ไม่ถูกต้อง")
        return

    recipe = next((r for r in data["recipes"] if r["id"] == recipe_id), None)
    if not recipe:
        print("❌ ไม่พบสูตร ID นี้")
        return

    print(f"\nกำลังแก้ไขสูตร: {recipe['name']}")
    print("1. แก้ไขชื่อสูตร/จำนวนเสิร์ฟ")
    print("2. แก้ไขวัตถุดิบในสูตร (ตั้งค่าใหม่ทั้งหมด)")
    print("0. ยกเลิก")

    choice = input("เลือก: ").strip()

    if choice == "1":
        name = input(f"  ชื่อสูตร [{recipe['name']}]: ").strip()
        servings = input(f"  จำนวนเสิร์ฟ [{recipe['servings']}]: ").strip()
        if name:
            recipe["name"] = name
        if servings:
            try:
                recipe["servings"] = int(servings)
            except ValueError:
                print("❌ จำนวนไม่ถูกต้อง")
        save_data(data)
        print("✅ แก้ไขสูตรเรียบร้อย")

    elif choice == "2":
        print("\n--- เลือกวัตถุดิบใหม่ ---")
        list_ingredients(data)
        new_ingredients = []
        while True:
            ing_input = input("\nระบุ ID วัตถุดิบ (หรือ Enter เพื่อเสร็จสิ้น): ").strip()
            if not ing_input:
                break
            try:
                ing_id = int(ing_input)
            except ValueError:
                print("❌ ID ไม่ถูกต้อง")
                continue
            ingredient = find_ingredient_by_id(data, ing_id)
            if not ingredient:
                print("❌ ไม่พบวัตถุดิบ ID นี้")
                continue
            if any(ri["ingredient_id"] == ing_id for ri in new_ingredients):
                print("⚠️  วัตถุดิบนี้ถูกเพิ่มแล้ว")
                continue
            try:
                qty = float(
                    input(f"จำนวน '{ingredient['name']}' ({ingredient['unit']}): ")
                )
            except ValueError:
                print("❌ จำนวนไม่ถูกต้อง")
                continue
            if qty <= 0:
                print("❌ จำนวนต้องมากกว่า 0")
                continue
            new_ingredients.append({"ingredient_id": ing_id, "quantity": qty})

        if new_ingredients:
            recipe["ingredients"] = new_ingredients
            save_data(data)
            print("✅ แก้ไขวัตถุดิบในสูตรเรียบร้อย")
        else:
            print("❌ ไม่มีวัตถุดิบ ยกเลิกการแก้ไข")


def delete_recipe(data):
    """ลบสูตรอาหาร"""
    list_recipes(data)
    if not data["recipes"]:
        return

    try:
        recipe_id = int(input("\nระบุ ID สูตรที่ต้องการลบ: "))
    except ValueError:
        print("❌ ID ไม่ถูกต้อง")
        return

    recipe = next((r for r in data["recipes"] if r["id"] == recipe_id), None)
    if not recipe:
        print("❌ ไม่พบสูตร ID นี้")
        return

    confirm = input(f"ยืนยันลบสูตร '{recipe['name']}'? (y/n): ").strip().lower()
    if confirm == "y":
        data["recipes"].remove(recipe)
        save_data(data)
        print(f"✅ ลบสูตร '{recipe['name']}' เรียบร้อย")
    else:
        print("ยกเลิกการลบ")


# ==================== คำนวณต้นทุน ====================

def calculate_recipe_cost(data, recipe):
    """คำนวณต้นทุนของสูตร"""
    total = 0.0
    for item in recipe["ingredients"]:
        ing = find_ingredient_by_id(data, item["ingredient_id"])
        if ing:
            total += item["quantity"] * ing["price_per_unit"]
    return total


def show_cost_detail(data):
    """แสดงรายละเอียดต้นทุนของสูตร"""
    list_recipes(data)
    if not data["recipes"]:
        return

    try:
        recipe_id = int(input("\nระบุ ID สูตรที่ต้องการดูต้นทุน: "))
    except ValueError:
        print("❌ ID ไม่ถูกต้อง")
        return

    recipe = next((r for r in data["recipes"] if r["id"] == recipe_id), None)
    if not recipe:
        print("❌ ไม่พบสูตร ID นี้")
        return

    print(f"\n===== ต้นทุนสูตร: {recipe['name']} =====")
    print(f"จำนวนเสิร์ฟต่อสูตร: {recipe['servings']}")
    print(f"\n{'วัตถุดิบ':<20} {'จำนวน':>8} {'หน่วย':<8} {'ราคา/หน่วย':>12} {'รวม':>12}")
    print("-" * 65)

    total = 0.0
    for item in recipe["ingredients"]:
        ing = find_ingredient_by_id(data, item["ingredient_id"])
        if ing:
            item_cost = item["quantity"] * ing["price_per_unit"]
            total += item_cost
            print(
                f"{ing['name']:<20} {item['quantity']:>8.2f} {ing['unit']:<8} "
                f"{ing['price_per_unit']:>10.2f}  {item_cost:>10.2f}"
            )

    print("-" * 65)
    print(f"{'ต้นทุนรวมต่อสูตร':>52} {total:>10.2f} บาท")
    cost_per_serving = total / recipe["servings"]
    print(f"{'ต้นทุนต่อเสิร์ฟ':>52} {cost_per_serving:>10.2f} บาท")

    # คำนวณราคาขายแนะนำ
    print("\n--- ราคาขายแนะนำ (ต่อเสิร์ฟ) ---")
    for margin_pct in [30, 50, 70, 100]:
        sell_price = cost_per_serving * (1 + margin_pct / 100)
        print(f"  กำไร {margin_pct}%: {sell_price:>10.2f} บาท")


def compare_costs(data):
    """เปรียบเทียบต้นทุนสูตรทั้งหมด"""
    if not data["recipes"]:
        print("\n(ยังไม่มีสูตรอาหาร)")
        return

    print("\n===== เปรียบเทียบต้นทุนสูตรทั้งหมด =====")
    print(f"{'ID':<5} {'ชื่อสูตร':<25} {'ต้นทุน/สูตร':>12} {'เสิร์ฟ':>6} {'ต้นทุน/เสิร์ฟ':>14}")
    print("-" * 65)

    for recipe in data["recipes"]:
        cost = calculate_recipe_cost(data, recipe)
        cost_per_serving = cost / recipe["servings"]
        print(
            f"{recipe['id']:<5} {recipe['name']:<25} {cost:>10.2f}  "
            f"{recipe['servings']:>6} {cost_per_serving:>12.2f}"
        )


# ==================== การผลิตและตัดสต๊อค ====================

def produce_recipe(data):
    """ผลิตตามสูตรและตัดสต๊อค"""
    list_recipes(data)
    if not data["recipes"]:
        return

    try:
        recipe_id = int(input("\nระบุ ID สูตรที่ต้องการผลิต: "))
    except ValueError:
        print("❌ ID ไม่ถูกต้อง")
        return

    recipe = next((r for r in data["recipes"] if r["id"] == recipe_id), None)
    if not recipe:
        print("❌ ไม่พบสูตร ID นี้")
        return

    try:
        batches = int(input(f"จำนวนรอบที่ต้องการผลิต (1 รอบ = {recipe['servings']} เสิร์ฟ): "))
    except ValueError:
        print("❌ จำนวนไม่ถูกต้อง")
        return

    if batches <= 0:
        print("❌ จำนวนต้องมากกว่า 0")
        return

    # ตรวจสอบว่าวัตถุดิบเพียงพอหรือไม่
    print(f"\n--- ตรวจสอบวัตถุดิบสำหรับ {batches} รอบ ---")
    can_produce = True
    shortage_list = []

    for item in recipe["ingredients"]:
        ing = find_ingredient_by_id(data, item["ingredient_id"])
        if not ing:
            print(f"❌ วัตถุดิบ ID {item['ingredient_id']} ถูกลบไปแล้ว ไม่สามารถผลิตได้")
            return

        needed = item["quantity"] * batches
        available = ing["stock"]
        status = "✅" if available >= needed else "❌"

        if available < needed:
            can_produce = False
            shortage = needed - available
            shortage_list.append(
                f"  {ing['name']}: ขาด {shortage:.2f} {ing['unit']}"
            )

        print(
            f"  {status} {ing['name']}: ต้องการ {needed:.2f} {ing['unit']} "
            f"| มี {available:.2f} {ing['unit']}"
        )

    if not can_produce:
        print("\n❌ วัตถุดิบไม่เพียงพอ:")
        for s in shortage_list:
            print(s)
        print("กรุณาเพิ่มสต๊อควัตถุดิบก่อนผลิต")
        return

    # ยืนยันการผลิต
    total_cost = calculate_recipe_cost(data, recipe) * batches
    total_servings = recipe["servings"] * batches
    print(f"\nสรุปการผลิต: {recipe['name']}")
    print(f"  จำนวน: {batches} รอบ = {total_servings} เสิร์ฟ")
    print(f"  ต้นทุนรวม: {total_cost:.2f} บาท")

    confirm = input("ยืนยันการผลิตและตัดสต๊อค? (y/n): ").strip().lower()
    if confirm != "y":
        print("ยกเลิกการผลิต")
        return

    # ตัดสต๊อค
    for item in recipe["ingredients"]:
        ing = find_ingredient_by_id(data, item["ingredient_id"])
        needed = item["quantity"] * batches
        ing["stock"] -= needed

    # บันทึกประวัติการผลิต
    from datetime import datetime

    log_entry = {
        "id": get_next_id(data["production_log"]),
        "recipe_id": recipe["id"],
        "recipe_name": recipe["name"],
        "batches": batches,
        "total_servings": total_servings,
        "total_cost": round(total_cost, 2),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    data["production_log"].append(log_entry)

    save_data(data)
    print(f"\n✅ ผลิตเสร็จสิ้น! ตัดสต๊อคเรียบร้อย")
    print(f"   สูตร: {recipe['name']}")
    print(f"   ผลิต: {total_servings} เสิร์ฟ")
    print(f"   ต้นทุน: {total_cost:.2f} บาท")


def check_producible(data):
    """ตรวจสอบว่าสูตรไหนผลิตได้กี่รอบ"""
    if not data["recipes"]:
        print("\n(ยังไม่มีสูตรอาหาร)")
        return

    print("\n===== ตรวจสอบความสามารถในการผลิต =====")
    for recipe in data["recipes"]:
        max_batches = float("inf")
        limiting_ingredient = ""

        for item in recipe["ingredients"]:
            ing = find_ingredient_by_id(data, item["ingredient_id"])
            if not ing:
                max_batches = 0
                limiting_ingredient = f"[วัตถุดิบ ID {item['ingredient_id']} ถูกลบ]"
                break
            if item["quantity"] > 0:
                possible = ing["stock"] / item["quantity"]
                if possible < max_batches:
                    max_batches = possible
                    limiting_ingredient = ing["name"]

        max_batches = int(max_batches) if max_batches != float("inf") else 0
        total_servings = max_batches * recipe["servings"]

        print(f"\n[{recipe['name']}]")
        print(f"  ผลิตได้สูงสุด: {max_batches} รอบ ({total_servings} เสิร์ฟ)")
        if max_batches > 0:
            print(f"  วัตถุดิบที่จำกัด: {limiting_ingredient}")
        elif limiting_ingredient:
            print(f"  สาเหตุ: {limiting_ingredient}")


def show_production_log(data):
    """แสดงประวัติการผลิต"""
    print("\n===== ประวัติการผลิต =====")
    if not data["production_log"]:
        print("(ยังไม่มีประวัติการผลิต)")
        return

    total_all_cost = 0.0
    print(f"{'ID':<5} {'วันที่':<22} {'สูตร':<20} {'รอบ':>5} {'เสิร์ฟ':>7} {'ต้นทุน':>12}")
    print("-" * 75)
    for log in data["production_log"]:
        total_all_cost += log["total_cost"]
        print(
            f"{log['id']:<5} {log['date']:<22} {log['recipe_name']:<20} "
            f"{log['batches']:>5} {log['total_servings']:>7} {log['total_cost']:>10.2f}"
        )
    print("-" * 75)
    print(f"{'ต้นทุนรวมทั้งหมด':>62} {total_all_cost:>10.2f} บาท")


# ==================== เมนูหลัก ====================

def ingredient_menu(data):
    """เมนูจัดการวัตถุดิบ"""
    while True:
        print("\n╔══════════════════════════════╗")
        print("║    จัดการวัตถุดิบ            ║")
        print("╠══════════════════════════════╣")
        print("║  1. ดูรายการวัตถุดิบ         ║")
        print("║  2. เพิ่มวัตถุดิบ            ║")
        print("║  3. แก้ไขวัตถุดิบ            ║")
        print("║  4. ลบวัตถุดิบ               ║")
        print("║  5. เพิ่มสต๊อค              ║")
        print("║  0. กลับเมนูหลัก            ║")
        print("╚══════════════════════════════╝")

        choice = input("เลือกเมนู: ").strip()
        if choice == "1":
            list_ingredients(data)
        elif choice == "2":
            add_ingredient(data)
        elif choice == "3":
            edit_ingredient(data)
        elif choice == "4":
            delete_ingredient(data)
        elif choice == "5":
            restock_ingredient(data)
        elif choice == "0":
            break
        else:
            print("❌ เมนูไม่ถูกต้อง")


def recipe_menu(data):
    """เมนูจัดการสูตรอาหาร"""
    while True:
        print("\n╔══════════════════════════════╗")
        print("║    จัดการสูตรอาหาร           ║")
        print("╠══════════════════════════════╣")
        print("║  1. ดูรายการสูตรอาหาร        ║")
        print("║  2. เพิ่มสูตรอาหาร           ║")
        print("║  3. แก้ไขสูตรอาหาร           ║")
        print("║  4. ลบสูตรอาหาร              ║")
        print("║  0. กลับเมนูหลัก            ║")
        print("╚══════════════════════════════╝")

        choice = input("เลือกเมนู: ").strip()
        if choice == "1":
            list_recipes(data)
        elif choice == "2":
            add_recipe(data)
        elif choice == "3":
            edit_recipe(data)
        elif choice == "4":
            delete_recipe(data)
        elif choice == "0":
            break
        else:
            print("❌ เมนูไม่ถูกต้อง")


def cost_menu(data):
    """เมนูคำนวณต้นทุน"""
    while True:
        print("\n╔══════════════════════════════╗")
        print("║    คำนวณต้นทุน              ║")
        print("╠══════════════════════════════╣")
        print("║  1. ดูต้นทุนรายสูตร          ║")
        print("║  2. เปรียบเทียบต้นทุนทุกสูตร ║")
        print("║  0. กลับเมนูหลัก            ║")
        print("╚══════════════════════════════╝")

        choice = input("เลือกเมนู: ").strip()
        if choice == "1":
            show_cost_detail(data)
        elif choice == "2":
            compare_costs(data)
        elif choice == "0":
            break
        else:
            print("❌ เมนูไม่ถูกต้อง")


def production_menu(data):
    """เมนูการผลิต"""
    while True:
        print("\n╔══════════════════════════════╗")
        print("║    การผลิตและสต๊อค           ║")
        print("╠══════════════════════════════╣")
        print("║  1. ผลิตตามสูตร (ตัดสต๊อค)   ║")
        print("║  2. ตรวจสอบผลิตได้กี่รอบ     ║")
        print("║  3. ประวัติการผลิต           ║")
        print("║  0. กลับเมนูหลัก            ║")
        print("╚══════════════════════════════╝")

        choice = input("เลือกเมนู: ").strip()
        if choice == "1":
            produce_recipe(data)
        elif choice == "2":
            check_producible(data)
        elif choice == "3":
            show_production_log(data)
        elif choice == "0":
            break
        else:
            print("❌ เมนูไม่ถูกต้อง")


def main():
    """โปรแกรมหลัก"""
    data = load_data()

    print("╔═══════════════════════════════════════╗")
    print("║  ระบบจัดการสูตรอาหาร                  ║")
    print("║  Recipe Management System             ║")
    print("╚═══════════════════════════════════════╝")

    while True:
        print("\n╔══════════════════════════════╗")
        print("║       เมนูหลัก              ║")
        print("╠══════════════════════════════╣")
        print("║  1. จัดการวัตถุดิบ           ║")
        print("║  2. จัดการสูตรอาหาร          ║")
        print("║  3. คำนวณต้นทุน             ║")
        print("║  4. การผลิตและสต๊อค          ║")
        print("║  0. ออกจากโปรแกรม           ║")
        print("╚══════════════════════════════╝")

        choice = input("เลือกเมนู: ").strip()

        if choice == "1":
            ingredient_menu(data)
        elif choice == "2":
            recipe_menu(data)
        elif choice == "3":
            cost_menu(data)
        elif choice == "4":
            production_menu(data)
        elif choice == "0":
            print("\nขอบคุณที่ใช้งาน! 👋")
            break
        else:
            print("❌ เมนูไม่ถูกต้อง")


if __name__ == "__main__":
    main()
