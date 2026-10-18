"""Run a repeatable full baseline extraction-count check."""
from src.extractor import DataExtractor
from src.watermark import WatermarkManager


def main():
    extractor = DataExtractor("telecom.db")
    watermark_mgr = WatermarkManager("telecom.db")

    # This baseline intentionally replays all rows on every run.
    watermark_mgr.reset_watermarks()

    print("\n" + "=" * 69)
    print("PART 1: INTEGRATION BASELINE TEST")
    print("=" * 69)

    print("\n BEFORE EXTRACTION:")
    watermark_mgr.show_all_watermarks()

    print("\n EXTRACTING DATA...")
    result_subs = extractor.extract_subscribers()
    result_cdr = extractor.extract_cdr()
    result_trans = extractor.extract_transactions()

    print("\n AFTER EXTRACTION:")
    watermark_mgr.show_all_watermarks()

    print("\n" + "=" * 69)
    print("EXTRACTION SUMMARY")
    print("=" * 69)
    print(f"Subscribers extracted: {result_subs['records_extracted']:,}")
    print(f"CDR records extracted: {result_cdr['records_extracted']:,}")
    print(f"Transactions extracted: {result_trans['records_extracted']:,}")
    print("\nAll extractions complete!")


if __name__ == "__main__":
    main()
