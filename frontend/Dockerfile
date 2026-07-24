FROM php:8.2-apache

# Enable Apache modules for proxying and rewrites
RUN a2enmod proxy proxy_http rewrite

# Install pdo_mysql extension
RUN docker-php-ext-install pdo pdo_mysql

# Configure document root
ENV APACHE_DOCUMENT_ROOT /var/www/html
RUN sed -ri -e 's!/var/www/html!${APACHE_DOCUMENT_ROOT}!g' /etc/apache2/sites-available/*.conf
RUN sed -ri -e 's!/var/www/html!${APACHE_DOCUMENT_ROOT}!g' /etc/apache2/apache2.conf /etc/apache2/conf-depth/*.conf 2>/dev/null || true

EXPOSE 80

