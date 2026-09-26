from django.db import migrations

CREATE_VIEW_SQL = """
CREATE VIEW v_sale_balances AS
SELECT
  s.id AS sale_id,
  s.client_id,
  COALESCE(l.total, 0)                          AS total,
  COALESCE(a.paid, 0)                           AS paid,
  COALESCE(l.total, 0) - COALESCE(a.paid, 0)    AS balance,
  CASE
    WHEN COALESCE(a.paid, 0) = 0                     THEN 'non_paye'
    WHEN COALESCE(a.paid, 0) >= COALESCE(l.total, 0) THEN 'solde'
    ELSE 'partiel'
  END                                            AS status
FROM core_sale s
LEFT JOIN (SELECT sale_id, SUM(unit_price * quantity) AS total
           FROM core_saleline GROUP BY sale_id) l ON l.sale_id = s.id
LEFT JOIN (SELECT sale_id, SUM(amount) AS paid
           FROM core_paymentallocation GROUP BY sale_id) a ON a.sale_id = s.id;
"""

DROP_VIEW_SQL = "DROP VIEW IF EXISTS v_sale_balances;"


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_salebalance_payment_paymentallocation'),
    ]

    operations = [
        migrations.RunSQL(sql=CREATE_VIEW_SQL, reverse_sql=DROP_VIEW_SQL),
    ]
