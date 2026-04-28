# AWS Shape Reference

Style pattern for resource icons:
```
outlineConnect=0;fontColor=#232F3E;gradientColor=none;strokeColor=none;
fillColor={COLOR};labelBackgroundColor=#ffffff;align=center;html=1;
fontSize=12;fontStyle=0;aspect=fixed;
shape=mxgraph.aws4.resourceIcon;resIcon={SHAPE};
```

## Service Keys

| Service key | resIcon | fillColor | Category |
|-------------|---------|-----------|----------|
| `lambda` | `mxgraph.aws4.lambda` | `#ED7100` | Compute |
| `api-gateway` | `mxgraph.aws4.api_gateway` | `#E7157B` | Integration |
| `s3` | `mxgraph.aws4.s3` | `#3F8624` | Storage |
| `rds` | `mxgraph.aws4.rds` | `#C7131F` | Database |
| `dynamodb` | `mxgraph.aws4.dynamodb` | `#C7131F` | Database |
| `elasticache` | `mxgraph.aws4.elasticache` | `#C7131F` | Database |
| `opensearch` | `mxgraph.aws4.opensearch_service` | `#0050D1` | Database |
| `ec2` | `mxgraph.aws4.ec2` | `#ED7100` | Compute |
| `ecs` | `mxgraph.aws4.ecs` | `#ED7100` | Compute |
| `eks` | `mxgraph.aws4.eks` | `#ED7100` | Compute |
| `fargate` | `mxgraph.aws4.fargate` | `#ED7100` | Compute |
| `ecr` | `mxgraph.aws4.ecr` | `#ED7100` | Compute |
| `cloudfront` | `mxgraph.aws4.cloudfront` | `#8C4FFF` | Networking |
| `route53` | `mxgraph.aws4.route_53` | `#8C4FFF` | Networking |
| `alb` | `mxgraph.aws4.application_load_balancer` | `#8C4FFF` | Networking |
| `nlb` | `mxgraph.aws4.network_load_balancer` | `#8C4FFF` | Networking |
| `waf` | `mxgraph.aws4.waf` | `#DD344C` | Security |
| `cognito` | `mxgraph.aws4.cognito` | `#DD344C` | Security |
| `iam` | `mxgraph.aws4.iam` | `#DD344C` | Security |
| `secrets-manager` | `mxgraph.aws4.secrets_manager` | `#DD344C` | Security |
| `kms` | `mxgraph.aws4.key_management_service` | `#DD344C` | Security |
| `sqs` | `mxgraph.aws4.sqs` | `#E7157B` | Integration |
| `sns` | `mxgraph.aws4.sns` | `#E7157B` | Integration |
| `eventbridge` | `mxgraph.aws4.eventbridge` | `#E7157B` | Integration |
| `step-functions` | `mxgraph.aws4.step_functions` | `#E7157B` | Integration |
| `kinesis` | `mxgraph.aws4.kinesis_data_streams` | `#8C4FFF` | Analytics |
| `cloudwatch` | `mxgraph.aws4.cloudwatch` | `#E7157B` | Management |
| `cloudtrail` | `mxgraph.aws4.cloudtrail` | `#E7157B` | Management |
| `codepipeline` | `mxgraph.aws4.codepipeline` | `#ED7100` | DevTools |
| `codebuild` | `mxgraph.aws4.codebuild` | `#ED7100` | DevTools |
| `codedeploy` | `mxgraph.aws4.codedeploy` | `#ED7100` | DevTools |
| `glue` | `mxgraph.aws4.glue` | `#8C4FFF` | Analytics |
| `athena` | `mxgraph.aws4.athena` | `#8C4FFF` | Analytics |
| `connect` | `mxgraph.aws4.connect` | `#E7157B` | Contact Center |

## Group Container Styles

| type | style |
|------|-------|
| `vpc` | `points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_vpc;strokeColor=#8C4FFF;fillColor=#F4F0FA;verticalLabelPosition=top;verticalAlign=bottom;align=center;spacingTop=25;fontColor=#8C4FFF;dashed=0;` |
| `region` | `points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_region;strokeColor=#147EBA;fillColor=#E6F2F8;verticalLabelPosition=top;verticalAlign=bottom;align=center;spacingTop=25;fontColor=#147EBA;dashed=1;` |
| `availability-zone` | `shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_availability_zone;strokeColor=#147EBA;fillColor=none;verticalLabelPosition=top;verticalAlign=bottom;align=center;spacingTop=25;fontColor=#147EBA;dashed=1;` |
| `generic` | `strokeColor=#666666;fillColor=#f5f5f5;verticalLabelPosition=top;verticalAlign=bottom;align=center;spacingTop=25;fontColor=#333333;dashed=1;rounded=1;` |
