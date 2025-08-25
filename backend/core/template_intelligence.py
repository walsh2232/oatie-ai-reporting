"""
AI-Powered Template Intelligence Engine
Advanced template generation, optimization, and performance analysis
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum
import json
import uuid
from dataclasses import dataclass, asdict

from pydantic import BaseModel


class TemplateType(str, Enum):
    """Template types supported by the intelligence engine"""
    TABULAR = "tabular"
    DASHBOARD = "dashboard"
    CHART = "chart"
    FORM = "form"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"


class DataType(str, Enum):
    """Data types for intelligent layout generation"""
    STRING = "string"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"


class LayoutRecommendation(str, Enum):
    """AI-powered layout recommendations"""
    SINGLE_COLUMN = "single_column"
    TWO_COLUMN = "two_column"
    GRID = "grid"
    DASHBOARD = "dashboard"
    CHART_HEAVY = "chart_heavy"
    TABLE_HEAVY = "table_heavy"


@dataclass
class SchemaField:
    """Database schema field representation"""
    name: str
    data_type: DataType
    nullable: bool = True
    primary_key: bool = False
    foreign_key: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None


@dataclass
class TableSchema:
    """Database table schema"""
    table_name: str
    fields: List[SchemaField]
    relationships: List[str] = None
    row_count: Optional[int] = None
    
    def __post_init__(self):
        if self.relationships is None:
            self.relationships = []


@dataclass
class PerformanceMetrics:
    """Performance analysis metrics"""
    execution_time_ms: float
    memory_usage_mb: float
    query_complexity: int
    cache_hit_ratio: float
    optimization_score: float
    bottlenecks: List[str] = None
    
    def __post_init__(self):
        if self.bottlenecks is None:
            self.bottlenecks = []


@dataclass
class TemplateVersion:
    """Template version control"""
    version_id: str
    template_id: str
    version_number: str
    created_at: datetime
    created_by: str
    changes: List[str]
    performance_metrics: Optional[PerformanceMetrics] = None
    is_active: bool = False


class TemplateIntelligenceEngine:
    """Main AI-powered template intelligence engine"""
    
    def __init__(self):
        self.template_cache: Dict[str, Any] = {}
        self.performance_cache: Dict[str, PerformanceMetrics] = {}
        self.version_store: Dict[str, List[TemplateVersion]] = {}
        
    async def analyze_schema(self, schema: TableSchema) -> Dict[str, Any]:
        """Analyze database schema and recommend template structure"""
        
        # AI-powered schema analysis
        field_analysis = []
        for field in schema.fields:
            analysis = {
                "field_name": field.name,
                "display_name": field.display_name or field.name.replace("_", " ").title(),
                "data_type": field.data_type,
                "recommended_widget": self._recommend_widget(field),
                "priority": self._calculate_field_priority(field),
                "formatting": self._recommend_formatting(field)
            }
            field_analysis.append(analysis)
        
        # Determine optimal template type
        template_type = self._recommend_template_type(schema)
        
        # Generate layout recommendation
        layout = self._recommend_layout(schema, field_analysis)
        
        return {
            "schema_analysis": {
                "table_name": schema.table_name,
                "field_count": len(schema.fields),
                "complexity_score": self._calculate_complexity(schema),
                "estimated_performance": self._estimate_performance(schema)
            },
            "template_recommendation": {
                "type": template_type,
                "layout": layout,
                "estimated_generation_time": self._estimate_generation_time(schema)
            },
            "field_analysis": field_analysis,
            "optimization_suggestions": self._generate_optimization_suggestions(schema)
        }
    
    async def generate_template(self, schema: TableSchema, template_type: TemplateType, 
                              user_preferences: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate Oracle BI Publisher template from schema analysis"""
        
        template_id = str(uuid.uuid4())
        
        # Generate template metadata
        metadata = {
            "template_id": template_id,
            "name": f"{schema.table_name.replace('_', ' ').title()} Report",
            "description": f"AI-generated template for {schema.table_name}",
            "type": template_type,
            "created_at": datetime.now(),
            "schema_source": schema.table_name,
            "ai_confidence": self._calculate_ai_confidence(schema, template_type)
        }
        
        # Generate template structure
        structure = await self._generate_template_structure(schema, template_type, user_preferences)
        
        # Generate Oracle BI Publisher RTF content
        rtf_content = await self._generate_rtf_template(schema, structure)
        
        # Generate sample data bindings
        data_bindings = self._generate_data_bindings(schema)
        
        # Performance optimization
        optimizations = await self._optimize_template_performance(schema, structure)
        
        template = {
            "metadata": metadata,
            "structure": structure,
            "rtf_content": rtf_content,
            "data_bindings": data_bindings,
            "optimizations": optimizations,
            "parameters": self._generate_template_parameters(schema),
            "preview_data": self._generate_preview_data(schema)
        }
        
        # Cache the template
        self.template_cache[template_id] = template
        
        return template
    
    async def optimize_template_performance(self, template_id: str, 
                                          current_metrics: Optional[PerformanceMetrics] = None) -> Dict[str, Any]:
        """Analyze and optimize template performance"""
        
        if template_id not in self.template_cache:
            raise ValueError(f"Template {template_id} not found")
        
        template = self.template_cache[template_id]
        
        # Performance analysis
        analysis = {
            "template_id": template_id,
            "current_performance": current_metrics,
            "optimization_recommendations": [],
            "estimated_improvements": {},
            "implementation_complexity": "medium"
        }
        
        # Query optimization recommendations
        if current_metrics and current_metrics.execution_time_ms > 2000:
            analysis["optimization_recommendations"].append({
                "type": "query_optimization",
                "description": "Add database indexes for primary query fields",
                "estimated_improvement": "40-60% faster execution",
                "implementation": "Create indexes on frequently queried columns"
            })
        
        # Memory optimization
        if current_metrics and current_metrics.memory_usage_mb > 100:
            analysis["optimization_recommendations"].append({
                "type": "memory_optimization",
                "description": "Implement pagination for large datasets",
                "estimated_improvement": "70% memory reduction",
                "implementation": "Add ROWNUM or OFFSET/FETCH pagination"
            })
        
        # Caching recommendations
        analysis["optimization_recommendations"].append({
            "type": "caching_strategy",
            "description": "Implement intelligent caching based on data volatility",
            "estimated_improvement": "80% faster subsequent loads",
            "implementation": "Cache static reference data, invalidate on schedule"
        })
        
        # Layout optimizations
        if template["structure"]["field_count"] > 20:
            analysis["optimization_recommendations"].append({
                "type": "layout_optimization",
                "description": "Use progressive disclosure for complex layouts",
                "estimated_improvement": "Improved user experience",
                "implementation": "Group fields into collapsible sections"
            })
        
        return analysis
    
    async def create_template_version(self, template_id: str, changes: List[str], 
                                    created_by: str) -> TemplateVersion:
        """Create a new version of an existing template"""
        
        if template_id not in self.version_store:
            self.version_store[template_id] = []
        
        versions = self.version_store[template_id]
        version_number = f"v{len(versions) + 1}.0"
        
        version = TemplateVersion(
            version_id=str(uuid.uuid4()),
            template_id=template_id,
            version_number=version_number,
            created_at=datetime.now(),
            created_by=created_by,
            changes=changes
        )
        
        versions.append(version)
        return version
    
    async def setup_ab_test(self, template_a_id: str, template_b_id: str,
                           test_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Setup A/B testing for template performance comparison"""
        
        test_id = str(uuid.uuid4())
        
        test_config = {
            "test_id": test_id,
            "template_a": template_a_id,
            "template_b": template_b_id,
            "created_at": datetime.now(),
            "status": "active",
            "criteria": test_criteria,
            "traffic_split": test_criteria.get("traffic_split", 50),
            "duration_days": test_criteria.get("duration_days", 14),
            "success_metrics": test_criteria.get("metrics", [
                "execution_time",
                "user_satisfaction",
                "error_rate"
            ])
        }
        
        return test_config
    
    def _recommend_widget(self, field: SchemaField) -> str:
        """Recommend appropriate UI widget for field"""
        widget_mapping = {
            DataType.STRING: "text_input",
            DataType.NUMBER: "number_input",
            DataType.DATE: "date_picker",
            DataType.BOOLEAN: "checkbox",
            DataType.CURRENCY: "currency_input",
            DataType.PERCENTAGE: "percentage_input"
        }
        return widget_mapping.get(field.data_type, "text_input")
    
    def _calculate_field_priority(self, field: SchemaField) -> int:
        """Calculate field display priority (1-10, 10 being highest)"""
        priority = 5  # Default
        
        if field.primary_key:
            priority += 3
        if field.name.lower() in ["name", "title", "description"]:
            priority += 2
        if not field.nullable:
            priority += 1
        if field.data_type in [DataType.CURRENCY, DataType.PERCENTAGE]:
            priority += 1
            
        return min(priority, 10)
    
    def _recommend_formatting(self, field: SchemaField) -> Dict[str, Any]:
        """Recommend formatting options for field"""
        formatting = {
            DataType.CURRENCY: {"format": "currency", "precision": 2},
            DataType.PERCENTAGE: {"format": "percentage", "precision": 1},
            DataType.DATE: {"format": "MM/dd/yyyy"},
            DataType.NUMBER: {"format": "number", "precision": 0}
        }
        return formatting.get(field.data_type, {})
    
    def _recommend_template_type(self, schema: TableSchema) -> TemplateType:
        """AI-powered template type recommendation"""
        field_count = len(schema.fields)
        
        # Simple heuristics for template type recommendation
        if field_count <= 5:
            return TemplateType.FORM
        elif field_count <= 10:
            return TemplateType.TABULAR
        else:
            return TemplateType.DASHBOARD
    
    def _recommend_layout(self, schema: TableSchema, field_analysis: List[Dict]) -> LayoutRecommendation:
        """Recommend optimal layout based on field analysis"""
        field_count = len(field_analysis)
        
        if field_count <= 3:
            return LayoutRecommendation.SINGLE_COLUMN
        elif field_count <= 8:
            return LayoutRecommendation.TWO_COLUMN
        else:
            return LayoutRecommendation.GRID
    
    def _calculate_complexity(self, schema: TableSchema) -> float:
        """Calculate schema complexity score (0-1)"""
        base_score = len(schema.fields) / 20  # Normalize to 20 fields max
        relationship_score = len(schema.relationships) / 10
        return min(base_score + relationship_score, 1.0)
    
    def _estimate_performance(self, schema: TableSchema) -> Dict[str, Any]:
        """Estimate template performance metrics"""
        complexity = self._calculate_complexity(schema)
        
        return {
            "estimated_execution_time_ms": int(1000 + (complexity * 3000)),
            "estimated_memory_mb": int(10 + (complexity * 50)),
            "optimization_potential": "high" if complexity > 0.7 else "medium"
        }
    
    def _estimate_generation_time(self, schema: TableSchema) -> float:
        """Estimate template generation time in seconds"""
        return 2.0 + (len(schema.fields) * 0.1)
    
    def _generate_optimization_suggestions(self, schema: TableSchema) -> List[Dict[str, str]]:
        """Generate optimization suggestions for schema"""
        suggestions = []
        
        if len(schema.fields) > 15:
            suggestions.append({
                "type": "field_reduction",
                "suggestion": "Consider grouping related fields or using progressive disclosure"
            })
        
        if schema.row_count and schema.row_count > 10000:
            suggestions.append({
                "type": "pagination",
                "suggestion": "Implement pagination for large datasets"
            })
        
        return suggestions
    
    def _calculate_ai_confidence(self, schema: TableSchema, template_type: TemplateType) -> float:
        """Calculate AI confidence in template generation (0-1)"""
        base_confidence = 0.8
        
        # Adjust based on schema complexity
        complexity = self._calculate_complexity(schema)
        confidence_adjustment = -0.2 * complexity
        
        return max(base_confidence + confidence_adjustment, 0.5)
    
    async def _generate_template_structure(self, schema: TableSchema, template_type: TemplateType,
                                         user_preferences: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate detailed template structure"""
        return {
            "type": template_type,
            "layout": self._recommend_layout(schema, []),
            "sections": self._generate_template_sections(schema),
            "field_count": len(schema.fields),
            "uses_ai_optimization": True
        }
    
    def _generate_template_sections(self, schema: TableSchema) -> List[Dict[str, Any]]:
        """Generate template sections based on field grouping"""
        sections = [
            {
                "name": "Header",
                "type": "header",
                "fields": [f.name for f in schema.fields[:3]]
            },
            {
                "name": "Details",
                "type": "detail",
                "fields": [f.name for f in schema.fields[3:]]
            }
        ]
        return sections
    
    async def _generate_rtf_template(self, schema: TableSchema, structure: Dict[str, Any]) -> str:
        """Generate Oracle BI Publisher RTF template content"""
        # This would generate actual RTF content for Oracle BI Publisher
        # For now, return a template structure
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- AI-Generated Oracle BI Publisher Template -->
<!-- Schema: {schema.table_name} -->
<!-- Generated: {datetime.now()} -->
<template>
    <header>
        <title>{schema.table_name.replace('_', ' ').title()} Report</title>
    </header>
    <body>
        <!-- Dynamic field content would be generated here -->
        {self._generate_rtf_fields(schema)}
    </body>
</template>"""
    
    def _generate_rtf_fields(self, schema: TableSchema) -> str:
        """Generate RTF field content"""
        fields_rtf = ""
        for field in schema.fields:
            fields_rtf += f"        <field name='{field.name}' type='{field.data_type}'/>\n"
        return fields_rtf
    
    def _generate_data_bindings(self, schema: TableSchema) -> Dict[str, Any]:
        """Generate data binding configuration"""
        return {
            "data_source": schema.table_name,
            "bindings": [
                {
                    "field": field.name,
                    "xpath": f"//{schema.table_name}/{field.name}",
                    "type": field.data_type
                }
                for field in schema.fields
            ]
        }
    
    async def _optimize_template_performance(self, schema: TableSchema, 
                                           structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate performance optimizations for template"""
        optimizations = []
        
        if len(schema.fields) > 10:
            optimizations.append({
                "type": "field_optimization",
                "description": "Use selective field loading for better performance"
            })
        
        return optimizations
    
    def _generate_template_parameters(self, schema: TableSchema) -> List[Dict[str, Any]]:
        """Generate template parameters for user input"""
        parameters = [
            {
                "name": "date_range",
                "type": "date_range",
                "label": "Date Range",
                "required": True
            }
        ]
        
        # Add parameters based on common field patterns
        for field in schema.fields:
            if "region" in field.name.lower():
                parameters.append({
                    "name": field.name,
                    "type": "select",
                    "label": field.display_name or field.name.title(),
                    "options": ["North", "South", "East", "West"]
                })
        
        return parameters
    
    def _generate_preview_data(self, schema: TableSchema) -> List[Dict[str, Any]]:
        """Generate sample preview data"""
        sample_data = []
        
        for i in range(min(5, 3)):  # Generate 3 sample rows
            row = {}
            for field in schema.fields:
                row[field.name] = self._generate_sample_value(field)
            sample_data.append(row)
        
        return sample_data
    
    def _generate_sample_value(self, field: SchemaField) -> Any:
        """Generate sample value for field based on its type"""
        sample_values = {
            DataType.STRING: f"Sample {field.name}",
            DataType.NUMBER: 12345,
            DataType.DATE: "2024-01-15",
            DataType.BOOLEAN: True,
            DataType.CURRENCY: 1234.56,
            DataType.PERCENTAGE: 85.5
        }
        return sample_values.get(field.data_type, "Sample Value")