# Bank profile schema

银行配置只描述稳定的版式差异，不保存客户资料。建议字段：

```yaml
name: example-bank
date_patterns: ["YYYYMMDD", "YYYY-MM-DD"]
amount_column: first_numeric_after_description
balance_column: second_numeric_after_description
multiline_description: true
```

未知银行使用通用规则；如果日期、金额或余额无法确定，保留记录并标记 `待人工核验`。
