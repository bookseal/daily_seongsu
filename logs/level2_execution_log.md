# Level 2 Execution Log
- **Date**: 2025-01-29
- **Status**: Partially Successful (Features Generated, Upload Pending SQL)
- **Version**: v2.0_20250129

## Execution Summary
- **Subway Data**: Fetched ~1000 rows (2022-2025).
- **Weather Data**: Fetched 1109 days from Open-Meteo.
- **Merge**: Successfully merged on `date`.
- **Feature Engineering**:
    - Generated `lag_1d`, `lag_7d`.
    - Generated `lag_364d` (Yearly Seasonality).
    - Generated `rolling_7d_avg`.
    - Dropped 364 rows due to NaNs (Expected for yearly lag).
- **Final Row Count**: 636 rows.

## Sample Data (Tail)
| date       | total_traffic | lag_1d | lag_7d | lag_364d | rolling_7d_avg | version_id |
|:-----------|:--------------|:-------|:-------|:---------|:---------------|:-----------|
| 2025-11-30 | 92923         | 119327 | 102207 | 81216    | 118568         | v2.0...    |
| 2025-12-01 | 118204        | 92923  | 114757 | 114389   | 117242         | v2.0...    |
| 2025-12-02 | 120464        | 118204 | 119777 | 119632   | 117734         | v2.0...    |
| 2025-12-03 | 122112        | 120464 | 121045 | 119495   | 117651         | v2.0...    |
| 2025-12-04 | 122545        | 122112 | 117938 | 118536   | 116090         | v2.0...    |

## Errors / Action Required
- **Upload Failed**: Table `public.model_features` does not exist.
- **Action**: Run the provided SQL script in Supabase Dashboard.
