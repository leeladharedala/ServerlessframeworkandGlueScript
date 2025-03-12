import sys
import random
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from faker import Faker
from awsglue.utils import getResolvedOptions

spark = SparkSession.builder \
    .appName("GenerateFakeUsersRDD") \
    .config("spark.sql.parquet.compression.codec", "snappy") \
    .getOrCreate()

fake = Faker()

args = getResolvedOptions(sys.argv, ['S3_BUCKET'])


s3_bucket = f"s3://{args['S3_BUCKET']}"

user_profiles_path = "FakeUserData/Users"


NUM_USERS = 100000  


user_schema = StructType([
    StructField("user_id", StringType(), False),
    StructField("first_name", StringType(), False),
    StructField("last_name", StringType(), False),
    StructField("age", IntegerType(), False),
    StructField("email", StringType(), False),
    StructField("phone_number", StringType(), False),
    StructField("address", StringType(), False),
    StructField("city", StringType(), False),
    StructField("state", StringType(), False),
    StructField("postal_code", StringType(), False),
    StructField("country", StringType(), False),
])


def generate_user(index):
    return (
        f"user_{index}",  
        fake.first_name(),
        fake.last_name(),
        random.randint(18, 70),
        fake.email(),
        fake.phone_number(),
        fake.street_address(),
        fake.city(),
        fake.state(),
        fake.zipcode(),
        fake.country(),
    )


rdd_users = spark.sparkContext.parallelize(range(NUM_USERS)).map(generate_user)


df_users = spark.createDataFrame(rdd_users, schema=user_schema)


df_users.write.mode("overwrite").parquet(f"{s3_bucket}/{user_profiles_path}")
print(f"User Profiles written successfully to S3: {s3_bucket}/{user_profiles_path}")

spark.stop()