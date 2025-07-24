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
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='利用可能なコマンド')
    
    # add コマンド
    add_parser = subparsers.add_parser('add', help='学習記録を追加')
    add_parser.add_argument('title', help='学習タイトル')
    add_parser.add_argument('--content', help='学習内容')
    add_parser.add_argument('--time', type=int, default=0, help='学習時間（分）')
    add_parser.add_argument('--category', help='カテゴリ')
    add_parser.add_argument('--difficulty', type=int, choices=[1, 2, 3, 4, 5], default=1, help='難易度（1-5）')
    
    # list コマンド
    list_parser = subparsers.add_parser('list', help='学習記録一覧を表示')
    list_parser.add_argument('--limit', type=int, default=10, help='表示件数')
    
    # show コマンド
    show_parser = subparsers.add_parser('show', help='学習記録の詳細を表示')
    show_parser.add_argument('id', type=int, help='学習記録ID')
    
    # update コマンド
    update_parser = subparsers.add_parser('update', help='学習記録を更新')
    update_parser.add_argument('id', type=int, help='学習記録ID')
    update_parser.add_argument('--title', help='新しいタイトル')
    update_parser.add_argument('--content', help='新しい内容')
    update_parser.add_argument('--time', type=int, help='新しい学習時間（分）')
    update_parser.add_argument('--category', help='新しいカテゴリ')
    update_parser.add_argument('--difficulty', type=int, choices=[1, 2, 3, 4, 5], help='新しい難易度')
    
    # delete コマンド
    delete_parser = subparsers.add_parser('delete', help='学習記録を削除')
    delete_parser.add_argument('id', type=int, help='学習記録ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # データベースマネージャーを初期化
    db = DatabaseManager()
    
    try:
        if args.command == 'add':
            handle_add(db, args)
        elif args.command == 'list':
            handle_list(db, args)
        elif args.command == 'show':
            handle_show(db, args)
        elif args.command == 'update':
            handle_update(db, args)
        elif args.command == 'delete':
            handle_delete(db, args)
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
        difficulty=args.difficulty
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
    
    print(f"📚 学習記録一覧 (最新{min(args.limit, len(records))}件)")
    print("-" * 60)
    
    for record in records[:args.limit]:
        print(f"ID: {record.id} | {record.title}")
        print(f"   時間: {record.study_time}分 | カテゴリ: {record.category or '未設定'}")
        print(f"   難易度: {'⭐' * record.difficulty} | 作成日: {record.created_at.strftime('%Y-%m-%d %H:%M')}")
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
        update_data['title'] = args.title
    if args.content:
        update_data['content'] = args.content
    if args.time is not None:
        update_data['study_time'] = args.time
    if args.category:
        update_data['category'] = args.category
    if args.difficulty:
        update_data['difficulty'] = args.difficulty
    
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


if __name__ == "__main__":
    main()