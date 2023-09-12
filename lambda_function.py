from aws_cdk import (
    aws_sagemaker as sagemaker,
    core
)

class MySageMakerEndpoint(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # SageMakerモデルの作成
        model = sagemaker.CfnModel(
            self, "MyModel",
            execution_role_arn="arn:aws:iam::account-id:role/execution_role",
            primary_container=sagemaker.CfnModel.ContainerDefinitionProperty(
                image="your-docker-image",
                model_data_url="s3://path/to/model.tar.gz"
            )
        )

        # エンドポイントの設定
        endpoint_config = sagemaker.CfnEndpointConfig(
            self, "MyEndpointConfig",
            production_variants=[
                sagemaker.CfnEndpointConfig.ProductionVariantProperty(
                    model_name=model.attr_model_name,
                    instance_type="ml.m5.large",
                    initial_variant_weight=1
                )
            ]
        )

        # エンドポイントの作成
        sagemaker.CfnEndpoint(
            self, "MyEndpoint",
            endpoint_config_name=endpoint_config.attr_endpoint_config_name
        )

app = core.App()
MySageMakerEndpoint(app, "MySageMakerEndpoint")
app.synth()
