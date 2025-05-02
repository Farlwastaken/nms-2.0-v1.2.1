FROM grafana/grafana:11.5.2

ENV GF_SECURITY_ADMIN_USER=root

ENV GF_SECURITY_ALLOW_EMBEDDING=true
ENV GF_SERVER_SERVE_FROM_SUB_PATH=true
ENV GF_SERVE_FROM_SUB_PATH=true
ENV GF_DASHBOARDS_MIN_REFRESH_INTERVAL=1s

# Sensitive data hardcoded with ENV, consider alternatives for security
ENV GF_SECURITY_ADMIN_PASSWORD=root1234 
ENV GF_AUTH_DISABLE_SIGNOUT_MENU=true

EXPOSE 3000

ADD ./provisioning /etc/grafana/provisioning
ADD ./dashboards /var/lib/grafana/dashboards

# Command to start the application
CMD [ "grafana-server" ]