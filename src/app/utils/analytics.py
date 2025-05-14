import pandas as pd
import numpy as np
from typing import List, Dict, Any
from datetime import datetime, timedelta

def analyze_biometric_data(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Анализ биометрических данных
    """
    df = pd.DataFrame(data)
    
    analysis = {
        "total_records": len(data),
        "data_types": df["data_type"].value_counts().to_dict(),
        "creation_timeline": df.groupby(pd.Grouper(key="created_at", freq="D")).size().to_dict(),
        "metadata_stats": {}
    }
    
    if "data_metadata" in df.columns:
        metadata_df = pd.json_normalize(df["data_metadata"])
        for col in metadata_df.columns:
            if metadata_df[col].dtype in [np.int64, np.float64]:
                analysis["metadata_stats"][col] = {
                    "mean": metadata_df[col].mean(),
                    "std": metadata_df[col].std(),
                    "min": metadata_df[col].min(),
                    "max": metadata_df[col].max()
                }
    
    return analysis

def analyze_access_patterns(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Анализ паттернов доступа к данным
    """
    df = pd.DataFrame(logs)
    
    analysis = {
        "total_accesses": len(logs),
        "access_by_organization": df.groupby("organization_id")["id"].count().to_dict(),
        "access_by_action": df["action"].value_counts().to_dict(),
        "access_timeline": df.groupby(pd.Grouper(key="timestamp", freq="H")).size().to_dict()
    }
    
    return analysis

def generate_usage_report(data: List[Dict[str, Any]], period_days: int = 30) -> Dict[str, Any]:
    """
    Генерация отчета об использовании системы
    """
    df = pd.DataFrame(data)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=period_days)
    
    mask = (df["created_at"] >= start_date) & (df["created_at"] <= end_date)
    period_data = df.loc[mask]
    
    report = {
        "period": f"Last {period_days} days",
        "total_records": len(period_data),
        "active_users": period_data["user_id"].nunique(),
        "data_distribution": period_data["data_type"].value_counts().to_dict(),
        "daily_activity": period_data.groupby(pd.Grouper(key="created_at", freq="D")).size().to_dict()
    }
    
    return report 