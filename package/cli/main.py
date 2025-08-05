"""
CLIメインエントリーポイント

コマンドラインインターフェースのメイン機能を提供します。
"""

import argparse
import sys
from typing import Optional

from ..models.study_record import StudyRecord
from ..database.connection import DatabaseManager


def main():
    """CLIメイン関数"""
    parser = argparse.ArgumentParser(
        description="StudyTracker - 学習進捗管理ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  study-tracker add "Python学習" --content "FastAPIの基礎" --time 60 --category "プログラミング"
  study-tracker list
  study-tracker show 1
  study-tracker update 1 --title "新しいタイトル"
  study-tracker delete 1
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="利用可能なコマンド")

    # add コマンド
    add_parser = subparsers.add_parser("add", help="学習記録を追加")
    add_parser.add_argument("title", help="学習タイトル")
    add_parser.add_argument("--content", help="学習内容")
    add_parser.add_argument("--time", type=int, default=0, help="学習時間（分）")
    add_parser.add_argument("--category", help="カテゴリ")
    add_parser.add_argument(
        "--difficulty",
        type=int,
        choices=[1, 2, 3, 4, 5],
        default=1,
        help="難易度（1-5）",
    )

    # list コマンド
    list_parser = subparsers.add_parser("list", help="学習記録一覧を表示")
    list_parser.add_argument("--limit", type=int, default=10, help="表示件数")
    list_parser.add_argument("--category", help="カテゴリでフィルタリング")
    list_parser.add_argument(
        "--difficulty", type=int, choices=[1, 2, 3, 4, 5], help="難易度でフィルタリング"
    )
    list_parser.add_argument(
        "--min-time", type=int, help="最小学習時間（分）でフィルタリング"
    )
    list_parser.add_argument(
        "--max-time", type=int, help="最大学習時間（分）でフィルタリング"
    )
    list_parser.add_argument("--search", help="タイトル・内容でキーワード検索")
    list_parser.add_argument("--days", type=int, help="過去N日間の記録のみ表示")

    # show コマンド
    show_parser = subparsers.add_parser("show", help="学習記録の詳細を表示")
    show_parser.add_argument("id", type=int, help="学習記録ID")

    # update コマンド
    update_parser = subparsers.add_parser("update", help="学習記録を更新")
    update_parser.add_argument("id", type=int, help="学習記録ID")
    update_parser.add_argument("--title", help="新しいタイトル")
    update_parser.add_argument("--content", help="新しい内容")
    update_parser.add_argument("--time", type=int, help="新しい学習時間（分）")
    update_parser.add_argument("--category", help="新しいカテゴリ")
    update_parser.add_argument(
        "--difficulty", type=int, choices=[1, 2, 3, 4, 5], help="新しい難易度"
    )

    # delete コマンド
    delete_parser = subparsers.add_parser("delete", help="学習記録を削除")
    delete_parser.add_argument("id", type=int, help="学習記録ID")

    # stats コマンド
    stats_parser = subparsers.add_parser("stats", help="学習統計情報を表示")
    stats_parser.add_argument(
        "--category", action="store_true", help="カテゴリ別統計を表示"
    )
    stats_parser.add_argument(
        "--period",
        choices=["daily", "weekly", "monthly"],
        default="all",
        help="期間別統計",
    )
    stats_parser.add_argument(
        "--difficulty", action="store_true", help="難易度別統計を表示"
    )

    # search コマンド
    search_parser = subparsers.add_parser("search", help="学習記録を検索")
    search_parser.add_argument("keyword", help="検索キーワード")
    search_parser.add_argument(
        "--title-only", action="store_true", help="タイトルのみ検索"
    )
    search_parser.add_argument(
        "--content-only", action="store_true", help="内容のみ検索"
    )
    search_parser.add_argument(
        "--case-sensitive", action="store_true", help="大文字小文字を区別"
    )
    search_parser.add_argument("--limit", type=int, default=10, help="表示件数")

    # export コマンド
    export_parser = subparsers.add_parser("export", help="学習記録をエクスポート")
    export_parser.add_argument(
        "format", choices=["csv", "json", "txt"], help="エクスポート形式"
    )
    export_parser.add_argument("--output", "-o", help="出力ファイル名")
    export_parser.add_argument("--category", help="カテゴリでフィルタリング")
    export_parser.add_argument(
        "--difficulty", type=int, choices=[1, 2, 3, 4, 5], help="難易度でフィルタリング"
    )
    export_parser.add_argument(
        "--min-time", type=int, help="最小学習時間（分）でフィルタリング"
    )
    export_parser.add_argument(
        "--max-time", type=int, help="最大学習時間（分）でフィルタリング"
    )
    export_parser.add_argument("--days", type=int, help="過去N日間の記録のみ")
    export_parser.add_argument(
        "--all-fields", action="store_true", help="全フィールドをエクスポート"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # データベースマネージャーを初期化
    db = DatabaseManager()

    try:
        if args.command == "add":
            handle_add(db, args)
        elif args.command == "list":
            handle_list(db, args)
        elif args.command == "show":
            handle_show(db, args)
        elif args.command == "update":
            handle_update(db, args)
        elif args.command == "delete":
            handle_delete(db, args)
        elif args.command == "stats":
            handle_stats(db, args)
        elif args.command == "search":
            handle_search(db, args)
        elif args.command == "export":
            handle_export(db, args)
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)


def handle_add(db: DatabaseManager, args):
    """学習記録追加処理"""
    record = StudyRecord(
        title=args.title,
        content=args.content,
        study_time=args.time,
        category=args.category,
        difficulty=args.difficulty,
    )

    record_id = db.add_study_record(record)
    print(f"✅ 学習記録を追加しました (ID: {record_id})")
    print(f"   タイトル: {record.title}")
    print(f"   学習時間: {record.study_time}分 ({record.get_study_hours():.1f}時間)")


def handle_list(db: DatabaseManager, args):
    """学習記録一覧表示処理"""
    records = db.get_all_study_records()

    if not records:
        print("📝 学習記録がありません")
        return

    # フィルタリング処理
    filtered_records = filter_records(records, args)

    if not filtered_records:
        print("📝 条件に一致する学習記録がありません")
        return

    print(f"📚 学習記録一覧 (条件に一致: {len(filtered_records)}件)")
    print("-" * 60)

    for record in filtered_records[: args.limit]:
        print(f"ID: {record.id} | {record.title}")
        print(
            f"   時間: {record.study_time}分 | カテゴリ: {record.category or '未設定'}"
        )
        print(
            f"   難易度: {'⭐' * record.difficulty} | 作成日: {record.created_at.strftime('%Y-%m-%d %H:%M')}"
        )
        print()


def handle_show(db: DatabaseManager, args):
    """学習記録詳細表示処理"""
    record = db.get_study_record(args.id)

    if not record:
        print(f"❌ ID {args.id} の学習記録が見つかりません")
        return

    print(f"📖 学習記録詳細 (ID: {record.id})")
    print("-" * 40)
    print(f"タイトル: {record.title}")
    print(f"内容: {record.content or '未設定'}")
    print(f"学習時間: {record.study_time}分 ({record.get_study_hours():.1f}時間)")
    print(f"カテゴリ: {record.category or '未設定'}")
    print(f"難易度: {'⭐' * record.difficulty}")
    print(f"作成日: {record.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"更新日: {record.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")


def handle_update(db: DatabaseManager, args):
    """学習記録更新処理"""
    # 更新するフィールドを収集
    update_data = {}
    if args.title:
        update_data["title"] = args.title
    if args.content:
        update_data["content"] = args.content
    if args.time is not None:
        update_data["study_time"] = args.time
    if args.category:
        update_data["category"] = args.category
    if args.difficulty:
        update_data["difficulty"] = args.difficulty

    if not update_data:
        print("❌ 更新するフィールドが指定されていません")
        return

    success = db.update_study_record(args.id, **update_data)

    if success:
        print(f"✅ 学習記録 (ID: {args.id}) を更新しました")
    else:
        print(f"❌ 学習記録 (ID: {args.id}) の更新に失敗しました")


def handle_delete(db: DatabaseManager, args):
    """学習記録削除処理"""
    success = db.delete_study_record(args.id)

    if success:
        print(f"✅ 学習記録 (ID: {args.id}) を削除しました")
    else:
        print(f"❌ 学習記録 (ID: {args.id}) の削除に失敗しました")


def handle_stats(db: DatabaseManager, args):
    """学習統計情報表示処理"""
    records = db.get_all_study_records()

    if not records:
        print("📊 学習統計")
        print("-" * 40)
        print("学習記録がありません")
        return

    # 基本統計
    total_records = len(records)
    total_time = sum(record.study_time for record in records)
    total_hours = total_time / 60
    avg_difficulty = sum(record.difficulty for record in records) / total_records

    print("📊 学習統計サマリー")
    print("-" * 40)
    print(f"総学習記録数: {total_records}件")
    print(f"総学習時間: {total_time}分 ({total_hours:.1f}時間)")
    print(f"平均難易度: {avg_difficulty:.1f} ({'⭐' * round(avg_difficulty)})")
    print(
        f"学習期間: {min(record.created_at for record in records).strftime('%Y-%m-%d')} 〜 {max(record.created_at for record in records).strftime('%Y-%m-%d')}"
    )
    print()

    # カテゴリ別統計
    if args.category:
        print("📂 カテゴリ別統計")
        print("-" * 40)
        categories = {}
        for record in records:
            category = record.category or "未分類"
            if category not in categories:
                categories[category] = {
                    "count": 0,
                    "total_time": 0,
                    "avg_difficulty": 0,
                }
            categories[category]["count"] += 1
            categories[category]["total_time"] += record.study_time
            categories[category]["avg_difficulty"] += record.difficulty

        for category, stats in categories.items():
            avg_diff = stats["avg_difficulty"] / stats["count"]
            print(f"{category}:")
            print(f"  記録数: {stats['count']}件")
            print(
                f"  学習時間: {stats['total_time']}分 ({stats['total_time']/60:.1f}時間)"
            )
            print(f"  平均難易度: {avg_diff:.1f} ({'⭐' * round(avg_diff)})")
            print()

    # 難易度別統計
    if args.difficulty:
        print("⭐ 難易度別統計")
        print("-" * 40)
        difficulty_stats = {}
        for i in range(1, 6):
            difficulty_stats[i] = {"count": 0, "total_time": 0}

        for record in records:
            difficulty_stats[record.difficulty]["count"] += 1
            difficulty_stats[record.difficulty]["total_time"] += record.study_time

        for difficulty, stats in difficulty_stats.items():
            if stats["count"] > 0:
                print(f"難易度 {difficulty} ({'⭐' * difficulty}):")
                print(f"  記録数: {stats['count']}件")
                print(
                    f"  学習時間: {stats['total_time']}分 ({stats['total_time']/60:.1f}時間)"
                )
                print()

    # 期間別統計
    if args.period != "all":
        print(f"📅 {args.period.title()}統計")
        print("-" * 40)
        from datetime import datetime, timedelta

        now = datetime.now()
        if args.period == "daily":
            start_date = now - timedelta(days=1)
            period_name = "今日"
        elif args.period == "weekly":
            start_date = now - timedelta(days=7)
            period_name = "過去7日間"
        elif args.period == "monthly":
            start_date = now - timedelta(days=30)
            period_name = "過去30日間"

        period_records = [r for r in records if r.created_at >= start_date]
        if period_records:
            period_time = sum(r.study_time for r in period_records)
            print(f"{period_name}の学習記録: {len(period_records)}件")
            print(
                f"{period_name}の学習時間: {period_time}分 ({period_time/60:.1f}時間)"
            )
        else:
            print(f"{period_name}の学習記録はありません")


def filter_records(records, args):
    """学習記録のフィルタリング処理"""
    filtered = records

    # カテゴリフィルタリング
    if hasattr(args, "category") and args.category:
        filtered = [
            r
            for r in filtered
            if r.category and args.category.lower() in r.category.lower()
        ]

    # 難易度フィルタリング
    if hasattr(args, "difficulty") and args.difficulty:
        filtered = [r for r in filtered if r.difficulty == args.difficulty]

    # 学習時間フィルタリング
    if hasattr(args, "min_time") and args.min_time:
        filtered = [r for r in filtered if r.study_time >= args.min_time]
    if hasattr(args, "max_time") and args.max_time:
        filtered = [r for r in filtered if r.study_time <= args.max_time]

    # キーワード検索
    if hasattr(args, "search") and args.search:
        search_term = args.search.lower()
        filtered = [
            r
            for r in filtered
            if search_term in r.title.lower()
            or (r.content and search_term in r.content.lower())
        ]

    # 期間フィルタリング
    if hasattr(args, "days") and args.days:
        from datetime import datetime, timedelta

        cutoff_date = datetime.now() - timedelta(days=args.days)
        filtered = [r for r in filtered if r.created_at >= cutoff_date]

    return filtered


def handle_search(db: DatabaseManager, args):
    """学習記録検索処理"""
    records = db.get_all_study_records()

    if not records:
        print("📝 学習記録がありません")
        return

    # 検索処理
    search_term = args.keyword
    if not args.case_sensitive:
        search_term = search_term.lower()

    search_results = []
    for record in records:
        title_match = False
        content_match = False

        # タイトル検索
        if not args.content_only:
            title_text = record.title
            if not args.case_sensitive:
                title_text = title_text.lower()
            title_match = search_term in title_text

        # 内容検索
        if not args.title_only and record.content:
            content_text = record.content
            if not args.case_sensitive:
                content_text = content_text.lower()
            content_match = search_term in content_text

        if title_match or content_match:
            search_results.append(record)

    if not search_results:
        print(f"🔍 キーワード '{args.keyword}' に一致する学習記録がありません")
        return

    print(f"🔍 検索結果: '{args.keyword}' ({len(search_results)}件)")
    print("-" * 60)

    for record in search_results[: args.limit]:
        print(f"ID: {record.id} | {record.title}")
        print(
            f"   時間: {record.study_time}分 | カテゴリ: {record.category or '未設定'}"
        )
        print(
            f"   難易度: {'⭐' * record.difficulty} | 作成日: {record.created_at.strftime('%Y-%m-%d %H:%M')}"
        )
        if record.content:
            content_preview = (
                record.content[:50] + "..."
                if len(record.content) > 50
                else record.content
            )
            print(f"   内容: {content_preview}")
        print()


def handle_export(db: DatabaseManager, args):
    """学習記録エクスポート処理"""
    records = db.get_all_study_records()

    if not records:
        print("📝 エクスポートする学習記録がありません")
        return

    # フィルタリング処理
    filtered_records = filter_records(records, args)

    if not filtered_records:
        print("📝 条件に一致する学習記録がありません")
        return

    # 出力ファイル名の決定
    if args.output:
        filename = args.output
    else:
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"study_records_{timestamp}.{args.format}"

    # エクスポート処理
    try:
        if args.format == "csv":
            export_to_csv(filtered_records, filename, args.all_fields)
        elif args.format == "json":
            export_to_json(filtered_records, filename, args.all_fields)
        elif args.format == "txt":
            export_to_txt(filtered_records, filename, args.all_fields)

        print(f"✅ 学習記録をエクスポートしました: {filename}")
        print(f"   形式: {args.format.upper()}")
        print(f"   件数: {len(filtered_records)}件")

    except Exception as e:
        print(f"❌ エクスポートに失敗しました: {e}")
        return


def export_to_csv(records, filename, all_fields=False):
    """CSV形式でエクスポート"""
    import csv

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        if all_fields:
            fieldnames = [
                "ID",
                "タイトル",
                "内容",
                "学習時間(分)",
                "学習時間(時間)",
                "カテゴリ",
                "難易度",
                "作成日",
                "更新日",
            ]
        else:
            fieldnames = [
                "ID",
                "タイトル",
                "学習時間(分)",
                "カテゴリ",
                "難易度",
                "作成日",
            ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for record in records:
            row = {
                "ID": record.id,
                "タイトル": record.title,
                "学習時間(分)": record.study_time,
                "カテゴリ": record.category or "",
                "難易度": record.difficulty,
                "作成日": record.created_at.strftime("%Y-%m-%d %H:%M"),
            }

            if all_fields:
                row.update(
                    {
                        "内容": record.content or "",
                        "学習時間(時間)": f"{record.get_study_hours():.1f}",
                        "更新日": record.updated_at.strftime("%Y-%m-%d %H:%M"),
                    }
                )

            writer.writerow(row)


def export_to_json(records, filename, all_fields=False):
    """JSON形式でエクスポート"""
    import json

    data = []
    for record in records:
        record_data = {
            "id": record.id,
            "title": record.title,
            "study_time_minutes": record.study_time,
            "study_time_hours": record.get_study_hours(),
            "category": record.category,
            "difficulty": record.difficulty,
            "created_at": record.created_at.isoformat(),
        }

        if all_fields:
            record_data.update(
                {"content": record.content, "updated_at": record.updated_at.isoformat()}
            )

        data.append(record_data)

    with open(filename, "w", encoding="utf-8") as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=False, indent=2)


def export_to_txt(records, filename, all_fields=False):
    """テキスト形式でエクスポート"""
    with open(filename, "w", encoding="utf-8") as txtfile:
        txtfile.write("StudyTracker - 学習記録エクスポート\n")
        txtfile.write("=" * 50 + "\n\n")

        for i, record in enumerate(records, 1):
            txtfile.write(f"記録 {i}: ID {record.id}\n")
            txtfile.write(f"タイトル: {record.title}\n")
            txtfile.write(
                f"学習時間: {record.study_time}分 ({record.get_study_hours():.1f}時間)\n"
            )
            txtfile.write(f"カテゴリ: {record.category or '未設定'}\n")
            txtfile.write(f"難易度: {'⭐' * record.difficulty}\n")
            txtfile.write(f"作成日: {record.created_at.strftime('%Y-%m-%d %H:%M')}\n")

            if all_fields and record.content:
                txtfile.write(f"内容: {record.content}\n")

            txtfile.write("-" * 30 + "\n\n")


if __name__ == "__main__":
    main()
