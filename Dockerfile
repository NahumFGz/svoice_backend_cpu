FROM public.ecr.aws/lambda/python:3.8

# copy function code and models into /var/task
COPY ./ ${LAMBDA_TASK_ROOT}

# install our dependencies
RUN yum -y install libsndfile
RUN python3 -m pip install --no-cache-dir -r requirements.txt
ENV NUMBA_CACHE_DIR=/tmp

# Set the CMD to your handler 
CMD [ "handler.predict"]