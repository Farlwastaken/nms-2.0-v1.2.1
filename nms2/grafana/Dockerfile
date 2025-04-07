#creating a grafana image with custom configuration
FROM grafana/grafana:11.5.2

ENV GF_SECURITY_ADMIN_USER=root
ENV GF_SECURITY_ADMIN_PASSWORD=root1234
ENV GF_SECURITY_ALLOW_EMBEDDING=true
ENV GF_SERVER_SERVE_FROM_SUB_PATH=true
ENV GF_SERVE_FROM_SUB_PATH=true
ENV GF_AUTH_DISABLE_SIGNOUT_MENU=true
ENV GF_DASHBOARDS_MIN_REFRESH_INTERVAL=1s

RUN grafana cli plugins install volkovlabs-form-panel 5.1.0
RUN grafana cli plugins install grafana-mqtt-datasource 1.1.0-beta.3

EXPOSE 3000

ADD ./provisioning /etc/grafana/provisioning
ADD ./dashboards /var/lib/grafana/dashboards

CMD [ "grafana-server" ]