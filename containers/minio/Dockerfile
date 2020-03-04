FROM bitnami/minio

USER root

ENV MINIO_ACCESS_KEY=hoK9VPtVI7gK
ENV MINIO_SECRET_KEY=ogkGpxr7ULtq

ENV MINIO_DEFAULT_BUCKETS=sapsanshop

RUN sed -i '/.*minio_client_execute mb.*/a \                minio_client_execute policy set download "local/${b}"' /libminio.sh

USER 1001
