FROM  python:3.12.6-slim 

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create a non-root user
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 -ms /bin/bash appuser

# Install necessary packages
RUN pip3 install --no-cache-dir --upgrade pip virtualenv

# Switch to non-root user
USER appuser
WORKDIR /home/appuser

# Copy the local Streamlit app to the container
COPY packages/chat-frontend-streamlit/dist/chat_frontend_streamlit-1.0.0.tar.gz /home/appuser/
ENV STREAMLIT_SERVER_PORT=${STREAMLIT_SERVER_PORT:-8501}
# Create a virtual environment and install the app
ENV VIRTUAL_ENV=/home/appuser/venv
RUN virtualenv ${VIRTUAL_ENV} \
    && . ${VIRTUAL_ENV}/bin/activate \
    && pip install /home/appuser/chat_frontend_streamlit-1.0.0.tar.gz \
    && mkdir -p /home/appuser/app \
    && tar --strip-components=2 -xzf /home/appuser/chat_frontend_streamlit-1.0.0.tar.gz -C /home/appuser

# Expose the default Streamlit port
EXPOSE ${STREAMLIT_SERVER_PORT}

# Copy the run script
COPY packages/chat-frontend-streamlit/run.sh /home/appuser
ENTRYPOINT ["./run.sh"]