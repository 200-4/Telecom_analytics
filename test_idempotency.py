from src.extractor import DataExtractor
from src.watermark import WatermarkManager

def main():
    print("\n"+ "=" * 70)
    print("Running Idempotency Test:If ran twice should get same data")
    print("="*70)

    extractor = DataExtractor('telecom.db')
    watermark_mgr = WatermarkManager('telecom.db')

    #Run 1
    watermark_mgr.show_all_watermarks()
    result1_subs = extractor.extract_subscribers()
    result1_cdr = extractor.extract_cdr()
    result1_trans = extractor.extract_transactions()

    print(f"Run 1 results")
    print(f"Subscribers: {result1_subs['records_extracted']:,}")
    print(f"CDR: {result1_cdr['records_extracted']:,}")
    print(f"Transaction: {result1_trans['records_extracted']:,}")

    #Run 2 (immediately after)
    print("\n--- RUN 2 (Immediately after) ---")
    result2_subs = extractor.extract_subscribers()
    result2_cdr = extractor.extract_cdr()
    result2_trans = extractor.extract_transactions()

    print(f"Run 2 results")
    print(f"Subscribers: {result2_subs['records_extracted']:,}")
    print(f"CDR: {result2_cdr['records_extracted']:,}")
    print(f"Transaction: {result2_trans['records_extracted']:,}")

    #Verify
    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("="* 70)

    if (result2_subs['records_extracted'] == 0 and
        result2_cdr['records_extracted'] == 0 and
        result2_trans['records_extracted'] == 0):
        print("IDEMPOTENT: Second run got 0 rows(CORRECT)")
    else:
        print("NOT IDEMPOTENT:Second run got records (WRONG!)")
if __name__ == "__main__":
    main()

