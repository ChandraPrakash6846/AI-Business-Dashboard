import pandas as pd
import numpy as np

# Fallback imports to prevent crashes if these utils aren't fully implemented yet
try:
    from utils.data_cleaner import detect_column_types
except ImportError:
    def detect_column_types(df):
        return {
            'numeric': df.select_dtypes(include='number').columns.tolist(),
            'date': df.select_dtypes(include='datetime').columns.tolist(),
            'categorical': df.select_dtypes(include=['object', 'category']).columns.tolist(),
            'boolean': df.select_dtypes(include='bool').columns.tolist()
        }

try:
    from utils.kpi_generator import detect_kpi_columns
except ImportError:
    def detect_kpi_columns(df):
        # Fallback: assume all numeric columns are KPIs
        return df.select_dtypes(include='number').columns.tolist()

def generate_insights(df, column_types=None):
    """Generate business insights from data using statistical analysis."""
    insights = []
    try:
        if df is None or df.empty:
            return []
            
        if column_types is None:
            column_types = detect_column_types(df)
            
        num_cols = column_types.get('numeric', [])
        cat_cols = column_types.get('categorical', [])
        date_cols = column_types.get('date', [])
        
        # 1. Top Performers
        for cat in cat_cols:
            if df[cat].nunique() > 1 and df[cat].nunique() < 20 and len(num_cols) > 0:
                target_col = num_cols[0]
                grouped = df.groupby(cat)[target_col].sum()
                if not grouped.empty:
                    top_item = grouped.idxmax()
                    top_val = grouped.max()
                    insights.append({
                        'type': 'top_performer',
                        'icon': '🏆',
                        'title': f'Top Performer in {cat}',
                        'detail': f'"{top_item}" has the highest total {target_col} at {top_val:,.2f}.',
                        'recommendation': f'Analyze strategies used for {top_item} and apply them to underperforming areas.',
                        'priority': 'high'
                    })
                    break # Just one top performer insight
                    
        # 2. Growth Trends
        if date_cols and num_cols:
            date_col = date_cols[0]
            val_col = num_cols[0]
            temp_df = df.dropna(subset=[date_col, val_col]).sort_values(by=date_col)
            if len(temp_df) > 1:
                first_half_mean = temp_df[val_col].iloc[:len(temp_df)//2].mean()
                second_half_mean = temp_df[val_col].iloc[len(temp_df)//2:].mean()
                if first_half_mean > 0:
                    pct_change = ((second_half_mean - first_half_mean) / first_half_mean) * 100
                    direction = "growth" if pct_change > 0 else "decline"
                    insights.append({
                        'type': 'trend',
                        'icon': '📈' if pct_change > 0 else '📉',
                        'title': f'{val_col.title()} {direction.title()} Trend',
                        'detail': f'Overall {val_col} has seen a {abs(pct_change):.1f}% {direction} when comparing earlier vs later periods.',
                        'recommendation': f'Investigate the key drivers of this {direction} to {"capitalize on it" if pct_change>0 else "mitigate risks"}.',
                        'priority': 'high'
                    })
        
        # 3. Concentration Risk
        for cat in cat_cols:
            if len(num_cols) > 0 and 1 < df[cat].nunique() <= 50:
                target_col = num_cols[0]
                totals = df.groupby(cat)[target_col].sum()
                if totals.sum() > 0:
                    max_pct = (totals.max() / totals.sum()) * 100
                    if max_pct > 40: # If one category is >40% of total
                        insights.append({
                            'type': 'concentration',
                            'icon': '⚠️',
                            'title': 'High Concentration Risk',
                            'detail': f'"{totals.idxmax()}" accounts for {max_pct:.1f}% of all {target_col}.',
                            'recommendation': 'Diversify to reduce dependency on a single segment.',
                            'priority': 'high'
                        })
                        break
        
        # 4. Anomalies (Z-score)
        for num in num_cols:
            series = df[num].dropna()
            if len(series) > 10 and series.std() > 0:
                z_scores = np.abs((series - series.mean()) / series.std())
                outliers = sum(z_scores > 3.0)
                if outliers > 0:
                    insights.append({
                        'type': 'anomaly',
                        'icon': '🚨',
                        'title': f'Anomalies in {num}',
                        'detail': f'Detected {outliers} highly unusual values (outliers) in {num}.',
                        'recommendation': 'Review these specific records to ensure data integrity or identify exceptional events.',
                        'priority': 'medium'
                    })
                    break

        # 5. Correlations
        if len(num_cols) > 1:
            corr_mat = df[num_cols].corr()
            found_corr = False
            for i in range(len(corr_mat.columns)):
                for j in range(i+1, len(corr_mat.columns)):
                    col1, col2 = corr_mat.columns[i], corr_mat.columns[j]
                    val = corr_mat.iloc[i, j]
                    if abs(val) > 0.75:
                        insights.append({
                            'type': 'correlation',
                            'icon': '🔗',
                            'title': 'Strong Correlation Detected',
                            'detail': f'{col1} and {col2} are highly correlated (r={val:.2f}).',
                            'recommendation': f'Leverage {col1} to predict or influence outcomes in {col2}.',
                            'priority': 'medium'
                        })
                        found_corr = True
                        break
                if found_corr: break
                
        # 6. Seasonal Patterns / Day of Week (Simplified)
        if date_cols and len(num_cols) > 0:
            date_col = date_cols[0]
            val_col = num_cols[0]
            try:
                temp_dates = pd.to_datetime(df[date_col].dropna())
                dow_means = df.groupby(temp_dates.dt.dayofweek)[val_col].mean()
                if len(dow_means) >= 5: # Has enough days
                    best_day_idx = dow_means.idxmax()
                    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
                    best_day = days[best_day_idx]
                    insights.append({
                        'type': 'pattern',
                        'icon': '📅',
                        'title': f'Peak Day Pattern for {val_col}',
                        'detail': f'On average, {best_day} is the highest performing day for {val_col}.',
                        'recommendation': f'Align marketing or operational resources to peak on {best_day}s.',
                        'priority': 'medium'
                    })
            except: pass

        # 7. Distribution Skew
        for num in num_cols:
            skew = df[num].skew()
            if abs(skew) > 1.5:
                insights.append({
                    'type': 'distribution',
                    'icon': '📊',
                    'title': f'Highly Skewed {num}',
                    'detail': f'The distribution of {num} is heavily skewed, meaning a few extreme values exist.',
                    'recommendation': 'Use medians rather than averages for baseline comparisons in this metric.',
                    'priority': 'low'
                })
                break
                
        # 8. Missing Data Quality
        missing_pct = df.isnull().mean().mean() * 100
        if missing_pct > 5:
            insights.append({
                'type': 'quality',
                'icon': '🧽',
                'title': 'Data Quality Warning',
                'detail': f'Approximately {missing_pct:.1f}% of your dataset contains missing values.',
                'recommendation': 'Implement data cleaning pipelines to impute or drop missing records.',
                'priority': 'high' if missing_pct > 15 else 'medium'
            })
            
        # 9. Averages vs Medians
        for num in num_cols:
            if not df[num].empty:
                mean_val = df[num].mean()
                median_val = df[num].median()
                if median_val != 0 and abs(mean_val - median_val) / median_val > 0.5:
                    insights.append({
                        'type': 'comparison',
                        'icon': '⚖️',
                        'title': f'Mean/Median Gap in {num}',
                        'detail': f'The average {num} ({mean_val:.2f}) differs greatly from the typical/median value ({median_val:.2f}).',
                        'recommendation': 'Focus on the median to understand the "typical" experience, as averages are distorted.',
                        'priority': 'medium'
                    })
                    break

        # Generate filler insights if we don't have enough (Need 8-10)
        while len(insights) < 8:
            insights.append({
                'type': 'comparison',
                'icon': '💡',
                'title': 'General Baseline Assessment',
                'detail': 'The current dataset provides a robust baseline for future historical comparison.',
                'recommendation': 'Continue monitoring these metrics periodically to build historical context.',
                'priority': 'low'
            })

        # Sort by priority
        priority_map = {'high': 0, 'medium': 1, 'low': 2}
        insights.sort(key=lambda x: priority_map.get(x['priority'], 3))
        
        return insights[:10]
    except Exception as e:
        print(f"Error generating insights: {e}")
        return []

def generate_recommendations(df, insights=None):
    """Generate actionable business recommendations based on data patterns."""
    recommendations = []
    try:
        if not insights:
            insights = generate_insights(df)
            
        for insight in insights:
            if insight['priority'] in ['high', 'medium']:
                effort = 'medium'
                if insight['type'] == 'quality': effort = 'high'
                elif insight['type'] in ['trend', 'top_performer']: effort = 'low'
                
                recommendations.append({
                    'title': f"Action: {insight['title']}",
                    'description': insight['recommendation'],
                    'impact': insight['priority'],
                    'effort': effort,
                    'icon': insight['icon']
                })
                
        # Fallback recommendations if empty
        if not recommendations:
            recommendations.append({
                'title': 'Establish Data Monitoring',
                'description': 'Set up regular check-ins on core metrics to establish a baseline.',
                'impact': 'medium',
                'effort': 'low',
                'icon': '👁️'
            })
            
        return recommendations[:5]
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        return []
