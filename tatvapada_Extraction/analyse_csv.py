import pandas as pd
from pathlib import Path


def gather_stats(df: pd.DataFrame) -> dict:
    return {
        "total_tatvapada_entries": len(df),
        "distinct_authors": df["tatvapadakarara_hesaru"].nunique() if "tatvapadakarara_hesaru" in df else 0,
        "distinct_vibhag": df["vibhag"].nunique() if "vibhag" in df else 0,
        "per_author_counts": df[
            "tatvapadakarara_hesaru"].value_counts().to_dict() if "tatvapadakarara_hesaru" in df else {}
    }


def count_csv_files(folder: Path) -> int:
    return len(list(folder.glob("*.csv")))


def get_csv_folder() -> Path:
    default_folder = Path("output_csv/individual")

    folder = default_folder
    count = count_csv_files(folder)
    print(f"Default folder: '{folder}' contains {count} CSV file(s).")

    proceed = input("Proceed with this folder? (y/n): ").strip().lower()
    while proceed != "y":
        folder_input = input("Enter folder path containing CSV files: ").strip()
        folder = Path(folder_input)
        if not folder.is_dir():
            print(f"Invalid folder path: {folder}")
            continue
        count = count_csv_files(folder)
        if count == 0:
            print(f"No CSV files found in folder: {folder}")
            continue
        print(f"Folder '{folder}' contains {count} CSV file(s).")
        proceed = input("Proceed with this folder? (y/n): ").strip().lower()
    return folder


def analyse_folder(csv_folder: Path):
    csv_files = sorted(csv_folder.glob("*.csv"))
    if not csv_files:
        print(f"No CSV files found in folder: {csv_folder}")
        return

    consolidated_list = []
    total_rows = 0
    stats_rows = []

    for csv_path in csv_files:
        try:
            df = pd.read_csv(csv_path, encoding="utf-8-sig")
            df["source_file"] = csv_path.name
            consolidated_list.append(df)

            total_rows += len(df)
            print(f"Loaded {csv_path.name} with {len(df)} rows. Total rows so far: {total_rows}")

            stats = gather_stats(df)
            stats_row = {
                "source_file": csv_path.name,
                "total_tatvapada_entries": stats["total_tatvapada_entries"],
                "distinct_authors": stats["distinct_authors"],
                "distinct_vibhag": stats["distinct_vibhag"],
                "author_breakdown": "; ".join(f"{author}:{count}" for author, count in stats["per_author_counts"].items())
            }
            stats_rows.append(stats_row)

        except Exception as e:
            print(f"Error processing {csv_path.name}: {e}")

    # Create output directory if not exists
    output_dir = csv_folder.parent / "analysis_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    if consolidated_list:
        consolidated_df = pd.concat(consolidated_list, ignore_index=True)
        consolidated_csv_path = output_dir / "consolidated.csv"
        consolidated_df.to_csv(consolidated_csv_path, index=False, encoding="utf-8-sig")
        print(f"Consolidated CSV saved to: {consolidated_csv_path}")
        print(f"Total rows in consolidated CSV: {len(consolidated_df)}")
    else:
        print("No data to consolidate.")

    if stats_rows:
        stats_df = pd.DataFrame(stats_rows)
        stats_csv_path = output_dir / "stats.csv"
        stats_df.to_csv(stats_csv_path, index=False, encoding="utf-8-sig")
        print(f"Statistics summary saved to: {stats_csv_path}")


if __name__ == "__main__":
    csv_folder = get_csv_folder()
    print(f"Using CSV folder: {csv_folder}")
    analyse_folder(csv_folder)
