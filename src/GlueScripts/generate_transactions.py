import sys
import random
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, FloatType
from faker import Faker
from awsglue.utils import getResolvedOptions

spark = SparkSession.builder \
    .appName("GenerateFakeTransactionsRDD") \
    .config("spark.sql.parquet.compression.codec", "snappy") \
    .getOrCreate()

fake = Faker()


args = getResolvedOptions(sys.argv, ['S3_BUCKET'])


s3_bucket = f"s3://{args['S3_BUCKET']}"

user_profiles_path = "FakeUserData/Users"
transactions_path = "FakeUserData/Transactions"


NUM_TRANSACTIONS_PER_USER = (10, 100)


df_users = spark.read.parquet(f"{s3_bucket}/{user_profiles_path}").select("user_id")


transaction_schema = StructType([
    StructField("transaction_id", StringType(), False),
    StructField("user_id", StringType(), False),
    StructField("transaction_amount", FloatType(), False),
    StructField("transaction_date", StringType(), False),
    StructField("description", StringType(), False),
])


user_rdd = df_users.rdd.map(lambda row: row["user_id"])


def generate_transactions(user_id):
    num_transactions = random.randint(*NUM_TRANSACTIONS_PER_USER)
    return [
        (
            f"txn_{user_id}_{i}",  
            user_id,
            round(random.uniform(10.0, 1000.0), 2),
            fake.date_this_decade().strftime("%Y-%m-%d"),
            fake.sentence(nb_words=6),
        )
        for i in range(num_transactions)
    ]


rdd_transactions = user_rdd.flatMap(generate_transactions)


df_transactions = spark.createDataFrame(rdd_transactions, schema=transaction_schema)


df_transactions.write.mode("overwrite").parquet(f"{s3_bucket}/{transactions_path}")
print(f"Transactions written successfully to S3: {s3_bucket}/{transactions_path}")

spark.stop()