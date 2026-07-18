"""
DataInsight Agent 演示脚本

展示核心功能：
1. RAG 知识检索
2. SQL 数据查询
3. Agent 智能对话
"""

import sys
import io
from pathlib import Path

# 修复 Windows 控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目路径
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))


def demo_rag_search():
    """演示 RAG 知识检索功能"""
    print("=" * 60)
    print("演示 1: RAG 知识检索")
    print("=" * 60)

    from data_insight.rag.rag_tool import RAGTool
    import tempfile

    knowledge_dir = project_dir / "data_insight" / "knowledge"

    with tempfile.TemporaryDirectory() as tmpdir:
        rag = RAGTool(
            knowledge_dir=str(knowledge_dir),
            vector_store_dir=tmpdir
        )

        queries = [
            "GMV是什么意思？",
            "复购率怎么计算？",
            "会员转化率的定义",
        ]

        for query in queries:
            print(f"\n查询: {query}")
            result = rag.run({"query": query, "top_k": 2})
            if result.status.value == "success":
                # 只显示前300字符
                print(result.text[:300])
            else:
                print(f"错误: {result.text}")

    print("\n" + "-" * 60)


def demo_sql_query():
    """演示 SQL 数据查询功能"""
    print("\n" + "=" * 60)
    print("演示 2: SQL 数据查询")
    print("=" * 60)

    from data_insight.tools.db_connector_tool import DBConnectorTool

    db_path = str(project_dir / "data_insight" / "test_retail.db")

    if not Path(db_path).exists():
        print(f"[ERROR] 数据库不存在: {db_path}")
        print("请先运行: python -m data_insight.tools.create_test_db")
        return

    db_tool = DBConnectorTool(
        db_config={"database": db_path},
        db_type="sqlite"
    )

    queries = [
        ("总订单数", "SELECT COUNT(*) as total_orders FROM orders"),
        ("区域销售排行", """
            SELECT region,
                   COUNT(*) as order_count,
                   ROUND(SUM(order_amount), 2) as total_sales
            FROM orders
            GROUP BY region
            ORDER BY total_sales DESC
        """),
        ("热销商品TOP5", """
            SELECT product_name,
                   COUNT(*) as sales_count,
                   ROUND(SUM(order_amount), 2) as total_amount
            FROM orders
            GROUP BY product_name
            ORDER BY total_amount DESC
            LIMIT 5
        """),
    ]

    for name, sql in queries:
        print(f"\n{name}:")
        result = db_tool.run({"sql": sql})
        if result.status.value == "success":
            print(result.text)
        else:
            print(f"错误: {result.text}")

    print("\n" + "-" * 60)


def demo_agent_conversation():
    """演示 Agent 智能对话功能"""
    print("\n" + "=" * 60)
    print("演示 3: Agent 智能对话")
    print("=" * 60)

    from data_insight.config import (
        DB_CONFIG, DEFAULT_DB_TYPE, KNOWLEDGE_DIR, OUTPUT_DIR, MEMORY_DIR, MAX_STEPS
    )
    from data_insight.agents.insight_agent import InsightAgent

    # 检查 LLM 配置
    from data_insight.config import LLM_API_KEY
    if not LLM_API_KEY or LLM_API_KEY == "your-api-key-here":
        print("[SKIP] 未配置 LLM_API_KEY，跳过 Agent 演示")
        print("请在 .env 文件中配置 LLM_API_KEY")
        return

    # 获取数据库配置
    db_config = DB_CONFIG.get(DEFAULT_DB_TYPE, {})

    # 表结构信息
    table_schemas = {
        "orders": {
            "description": "订单表，记录所有销售订单",
            "columns": [
                {"name": "order_id", "type": "VARCHAR", "description": "订单ID"},
                {"name": "order_date", "type": "DATE", "description": "订单日期"},
                {"name": "region", "type": "VARCHAR", "description": "区域（华东/华北/华南/华西）"},
                {"name": "category", "type": "VARCHAR", "description": "商品品类"},
                {"name": "product_name", "type": "VARCHAR", "description": "商品名称"},
                {"name": "order_amount", "type": "DECIMAL", "description": "订单金额"},
                {"name": "customer_id", "type": "VARCHAR", "description": "客户ID"},
            ]
        }
    }

    # 创建 Agent
    agent = InsightAgent.create(
        db_config=db_config,
        db_type=DEFAULT_DB_TYPE,
        table_schemas=table_schemas,
        knowledge_dir=str(KNOWLEDGE_DIR),
        output_dir=str(OUTPUT_DIR),
        memory_dir=str(MEMORY_DIR),
        max_steps=5
    )

    # 演示查询
    demo_queries = [
        "查询各区域的销售总额",
        "GMV是什么意思？",
    ]

    for query in demo_queries:
        print(f"\n用户: {query}")
        print("-" * 40)
        try:
            result = agent.run(query)
            print(f"Agent: {result}")
        except Exception as e:
            print(f"错误: {e}")

    print("\n" + "-" * 60)


def main():
    """主演示函数"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   📊 DataInsight Agent 演示                                  ║
║   零售/电商数据分析智能体                                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # 演示 1: RAG 知识检索
    demo_rag_search()

    # 演示 2: SQL 数据查询
    demo_sql_query()

    # 演示 3: Agent 智能对话
    demo_agent_conversation()

    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ✅ 演示完成！                                               ║
║                                                              ║
║   启动完整交互模式:                                           ║
║   python -m data_insight.main                                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    main()
