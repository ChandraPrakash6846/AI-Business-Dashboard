import pandas as pd
import numpy as np
from scipy import stats

def trend_analysis(df, date_col, value_col, window_short=7, window_long=30):
    """Perform trend analysis with moving averages."""
    try:
        if df.empty or date_col not in df.columns or value_col not in df.columns:
            return {'error': 'Invalid DataFrame or columns not found.'}
            
        res_df = df.copy()
        # Convert to datetime just in case
        res_df[date_col] = pd.to_datetime(res_df[date_col], errors='coerce')
        res_df = res_df.dropna(subset=[date_col, value_col]).sort_values(by=date_col)
        
        if res_df.empty:
            return {'error': 'No valid date/value rows found.'}
            
        short_ma_col = f"{value_col}_MA_short"
        long_ma_col = f"{value_col}_MA_long"
        
        res_df[short_ma_col] = res_df[value_col].rolling(window=window_short, min_periods=1).mean()
        res_df[long_ma_col] = res_df[value_col].rolling(window=window_long, min_periods=1).mean()
        
        first_val = res_df[value_col].iloc[0]
        last_val = res_df[value_col].iloc[-1]
        
        growth_rate = ((last_val - first_val) / first_val * 100) if first_val != 0 else 0.0
        
        # Trend direction based on short MA
        first_short_ma = res_df[short_ma_col].iloc[0]
        last_short_ma = res_df[short_ma_col].iloc[-1]
        diff = last_short_ma - first_short_ma
        
        if diff > (first_short_ma * 0.05):
            direction = 'upward'
        elif diff < -(first_short_ma * 0.05):
            direction = 'downward'
        else:
            direction = 'stable'
            
        summary = f"The {value_col} shows a {direction} trend with an overall growth of {growth_rate:.2f}%."
        
        return {
            'trend_data': res_df,
            'growth_rate': growth_rate,
            'direction': direction,
            'summary': summary
        }
    except Exception as e:
        return {'error': str(e)}

def correlation_analysis(df):
    """Compute Pearson correlation matrix for all numeric columns."""
    try:
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty or numeric_df.shape[1] < 2:
            return {'error': 'Not enough numeric columns for correlation.'}
            
        corr_matrix = numeric_df.corr(method='pearson')
        
        strong_correlations = []
        cols = corr_matrix.columns
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                col1, col2 = cols[i], cols[j]
                val = corr_matrix.iloc[i, j]
                if abs(val) > 0.7 and not np.isnan(val):
                    strong_correlations.append((col1, col2, val))
                    
        strong_correlations.sort(key=lambda x: abs(x[2]), reverse=True)
        
        if strong_correlations:
            pairs = [f"{c1} & {c2} ({v:.2f})" for c1, c2, v in strong_correlations[:3]]
            summary = f"Found strong correlations between: {', '.join(pairs)}."
        else:
            summary = "No strong correlations (|r| > 0.7) found among numeric metrics."
            
        return {
            'matrix': corr_matrix,
            'strong_correlations': strong_correlations,
            'summary': summary
        }
    except Exception as e:
        return {'error': str(e)}

def anomaly_detection(df, column, threshold=2.0):
    """Detect anomalies using Z-score method."""
    try:
        if df.empty or column not in df.columns:
            return {'error': f"Column '{column}' not found or empty DataFrame."}
            
        series = df[column].dropna()
        if len(series) < 3:
            return {'error': 'Not enough data points for anomaly detection.'}
            
        mean_val = series.mean()
        std_val = series.std()
        
        # Handle zero standard deviation
        if std_val == 0:
            return {'error': 'Standard deviation is zero, cannot compute Z-scores.'}
            
        z_scores = (series - mean_val) / std_val
        
        anomaly_mask = np.abs(z_scores) > threshold
        anomalies_df = df.loc[series.index[anomaly_mask]].copy()
        anomalies_df['z_score'] = z_scores[anomaly_mask]
        
        count = len(anomalies_df)
        summary = f"Detected {count} anomalies in {column} exceeding a Z-score threshold of {threshold}."
        
        return {
            'anomalies': anomalies_df,
            'count': count,
            'column': column,
            'mean': mean_val,
            'std': std_val,
            'threshold': threshold,
            'summary': summary
        }
    except Exception as e:
        return {'error': str(e)}

def distribution_analysis(df, column):
    """Analyze distribution of a numeric column."""
    try:
        if df.empty or column not in df.columns:
            return {'error': f"Column '{column}' not found or empty DataFrame."}
            
        series = df[column].dropna()
        if len(series) < 3:
            return {'error': 'Not enough data points for distribution analysis.'}
            
        mean_val = series.mean()
        median_val = series.median()
        std_val = series.std()
        skewness = series.skew()
        kurt = series.kurtosis()
        
        q1 = series.quantile(0.25)
        q2 = median_val
        q3 = series.quantile(0.75)
        
        is_normal = False
        if len(series) >= 3 and len(series) < 5000:
            stat, p = stats.shapiro(series)
            is_normal = p > 0.05
        else:
            is_normal = abs(skewness) < 0.5
            
        shape_desc = "approximately normal" if is_normal else ("skewed" if abs(skewness) > 1 else "moderately skewed")
        summary = f"The distribution of {column} is {shape_desc} with a mean of {mean_val:.2f} and median of {median_val:.2f}."
        
        return {
            'mean': mean_val,
            'median': median_val,
            'std': std_val,
            'skewness': skewness,
            'kurtosis': kurt,
            'quartiles': {'Q1': q1, 'Q2': q2, 'Q3': q3},
            'is_normal': is_normal,
            'summary': summary
        }
    except Exception as e:
        return {'error': str(e)}
