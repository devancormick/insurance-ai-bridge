"""
Data Quality Framework
Data quality scoring, validation rules, profiling, and anomaly detection
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


class QualityLevel(Enum):
    """Data quality levels"""
    EXCELLENT = "excellent"  # 90-100%
    GOOD = "good"  # 70-89%
    FAIR = "fair"  # 50-69%
    POOR = "poor"  # <50%


@dataclass
class QualityRule:
    """Data quality validation rule"""
    name: str
    description: str
    validation_function: callable
    severity: str  # critical, warning, info
    enabled: bool = True


@dataclass
class QualityScore:
    """Data quality score"""
    overall_score: float
    completeness: float
    accuracy: float
    consistency: float
    timeliness: float
    validity: float
    level: QualityLevel
    violations: List[Dict[str, Any]]
    timestamp: datetime


class DataQualityFramework:
    """Data quality framework with scoring and monitoring"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.rules: List[QualityRule] = []
        self._initialize_rules()
    
    def _initialize_rules(self):
        """Initialize data quality rules"""
        # Completeness rules
        self.rules.append(QualityRule(
            name="required_fields_present",
            description="All required fields must be present",
            validation_function=self._check_required_fields,
            severity="critical",
            enabled=True
        ))
        
        # Accuracy rules
        self.rules.append(QualityRule(
            name="valid_data_types",
            description="Data types must match schema",
            validation_function=self._check_data_types,
            severity="critical",
            enabled=True
        ))
        
        # Consistency rules
        self.rules.append(QualityRule(
            name="referential_integrity",
            description="Foreign key relationships must be valid",
            validation_function=self._check_referential_integrity,
            severity="critical",
            enabled=True
        ))
        
        # Validity rules
        self.rules.append(QualityRule(
            name="value_ranges",
            description="Values must be within valid ranges",
            validation_function=self._check_value_ranges,
            severity="warning",
            enabled=True
        ))
    
    async def assess_quality(self, data: Dict[str, Any], schema: Optional[Dict[str, Any]] = None) -> QualityScore:
        """
        Assess data quality
        
        Args:
            data: Data dictionary to assess
            schema: Optional schema definition
        
        Returns:
            QualityScore with detailed metrics
        """
        violations = []
        scores = {
            "completeness": 100.0,
            "accuracy": 100.0,
            "consistency": 100.0,
            "timeliness": 100.0,
            "validity": 100.0
        }
        
        # Run quality rules
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            try:
                result = await rule.validation_function(data, schema)
                if not result.get("passed", True):
                    violations.append({
                        "rule": rule.name,
                        "description": rule.description,
                        "severity": rule.severity,
                        "details": result.get("details")
                    })
                    
                    # Deduct points based on severity
                    if rule.severity == "critical":
                        scores["validity"] -= 20
                    elif rule.severity == "warning":
                        scores["validity"] -= 10
                    else:
                        scores["validity"] -= 5
            except Exception as e:
                logger.error(f"Error running quality rule {rule.name}: {e}", exc_info=True)
        
        # Calculate completeness
        scores["completeness"] = self._calculate_completeness(data, schema)
        
        # Calculate overall score (weighted average)
        overall_score = (
            scores["completeness"] * 0.25 +
            scores["accuracy"] * 0.25 +
            scores["consistency"] * 0.20 +
            scores["timeliness"] * 0.15 +
            scores["validity"] * 0.15
        )
        
        # Determine quality level
        if overall_score >= 90:
            level = QualityLevel.EXCELLENT
        elif overall_score >= 70:
            level = QualityLevel.GOOD
        elif overall_score >= 50:
            level = QualityLevel.FAIR
        else:
            level = QualityLevel.POOR
        
        return QualityScore(
            overall_score=overall_score,
            completeness=scores["completeness"],
            accuracy=scores["accuracy"],
            consistency=scores["consistency"],
            timeliness=scores["timeliness"],
            validity=max(0, scores["validity"]),  # Ensure non-negative
            level=level,
            violations=violations,
            timestamp=datetime.utcnow()
        )
    
    def _calculate_completeness(self, data: Dict[str, Any], schema: Optional[Dict[str, Any]]) -> float:
        """Calculate data completeness score"""
        if not schema:
            return 100.0
        
        required_fields = schema.get("required", [])
        if not required_fields:
            return 100.0
        
        present_fields = sum(1 for field in required_fields if field in data and data[field] is not None)
        return (present_fields / len(required_fields)) * 100
    
    async def _check_required_fields(self, data: Dict[str, Any], schema: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Check if all required fields are present"""
        if not schema:
            return {"passed": True}
        
        required_fields = schema.get("required", [])
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        
        return {
            "passed": len(missing_fields) == 0,
            "details": {"missing_fields": missing_fields} if missing_fields else None
        }
    
    async def _check_data_types(self, data: Dict[str, Any], schema: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Check if data types match schema"""
        if not schema:
            return {"passed": True}
        
        type_violations = []
        properties = schema.get("properties", {})
        
        for field, value in data.items():
            if field in properties:
                expected_type = properties[field].get("type")
                actual_type = type(value).__name__
                
                if expected_type == "string" and actual_type != "str":
                    type_violations.append({"field": field, "expected": expected_type, "actual": actual_type})
                elif expected_type == "integer" and actual_type != "int":
                    type_violations.append({"field": field, "expected": expected_type, "actual": actual_type})
                elif expected_type == "number" and actual_type not in ["int", "float"]:
                    type_violations.append({"field": field, "expected": expected_type, "actual": actual_type})
        
        return {
            "passed": len(type_violations) == 0,
            "details": {"type_violations": type_violations} if type_violations else None
        }
    
    async def _check_referential_integrity(self, data: Dict[str, Any], schema: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Check referential integrity"""
        # Placeholder - real implementation would check foreign key relationships
        return {"passed": True}
    
    async def _check_value_ranges(self, data: Dict[str, Any], schema: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Check if values are within valid ranges"""
        if not schema:
            return {"passed": True}
        
        range_violations = []
        properties = schema.get("properties", {})
        
        for field, value in data.items():
            if field in properties:
                field_schema = properties[field]
                
                # Check minimum/maximum
                if "minimum" in field_schema and value < field_schema["minimum"]:
                    range_violations.append({
                        "field": field,
                        "value": value,
                        "constraint": f"minimum: {field_schema['minimum']}"
                    })
                
                if "maximum" in field_schema and value > field_schema["maximum"]:
                    range_violations.append({
                        "field": field,
                        "value": value,
                        "constraint": f"maximum: {field_schema['maximum']}"
                    })
                
                # Check enum values
                if "enum" in field_schema and value not in field_schema["enum"]:
                    range_violations.append({
                        "field": field,
                        "value": value,
                        "constraint": f"enum: {field_schema['enum']}"
                    })
        
        return {
            "passed": len(range_violations) == 0,
            "details": {"range_violations": range_violations} if range_violations else None
        }
    
    async def detect_anomalies(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect anomalies in dataset
        
        Args:
            data: List of data records
        
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        if len(data) < 2:
            return anomalies
        
        # Statistical anomaly detection (simplified)
        # Real implementation would use ML-based anomaly detection
        
        # Check for outliers in numeric fields
        numeric_fields = {}
        for record in data:
            for key, value in record.items():
                if isinstance(value, (int, float)):
                    if key not in numeric_fields:
                        numeric_fields[key] = []
                    numeric_fields[key].append(value)
        
        for field, values in numeric_fields.items():
            if len(values) < 3:
                continue
            
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            std_dev = variance ** 0.5
            
            # Identify outliers (beyond 2 standard deviations)
            for i, value in enumerate(values):
                if abs(value - mean) > 2 * std_dev:
                    anomalies.append({
                        "type": "outlier",
                        "field": field,
                        "value": value,
                        "record_index": i,
                        "mean": mean,
                        "std_dev": std_dev,
                        "severity": "warning"
                    })
        
        return anomalies


# Global data quality framework instance
data_quality_framework: Optional[DataQualityFramework] = None


def get_data_quality_framework() -> DataQualityFramework:
    """Get global data quality framework instance"""
    global data_quality_framework
    if data_quality_framework is None:
        from app.config import settings
        data_quality_framework = DataQualityFramework(settings.data_quality_config)
    return data_quality_framework


