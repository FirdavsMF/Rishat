Задание: 
----
* Реализовать Django + Stripe API бэкенд со следующим функционалом и условиями:
* Django Модель `Item` с полями `(name, description, price) `
* API с двумя методами:
    * GET `/buy/{id}`, c помощью которого можно получить Stripe Session Id для оплаты выбранного Item. При выполнении этого метода c бэкенда с помощью python библиотеки stripe должен выполняться запрос` stripe.checkout.Session.create(...)` и полученный session.id выдаваться в результате запроса
    * GET `/item/{id}`, c помощью которого можно получить простейшую HTML страницу, на которой будет информация о выбранном `Item` и кнопка Buy. По нажатию на кнопку Buy должен происходить запрос на `/buy/{id}`, получение session_id и далее  с помощью JS библиотеки Stripe происходить редирект на Checkout форму `stripe.redirectToCheckout(sessionId=session_id)`

* Залить решение на Github, описать запуск в README.md

* Использование `environment variables`

* Просмотр Django Моделей в Django Admin панели - __доступно по адресу `coxalah534.pythonanywhere.com/admin` user: `admin`, pass: `1`__

* Запуск приложения на удаленном сервере, доступном для тестирования - __запущенно на `coxalah534.pythonanywhere.com`__

* Модель Order, в которой можно объединить несколько Item и сделать платёж в Stripe на содержимое Order c общей стоимостью всех Items

* Модели Discount, Tax, которые можно прикрепить к модели Order и связать с соответствующими атрибутами при создании платежа в Stripe - в таком случае они корректно отображаются в Stripe Checkout форме

* Добавить поле Item.currency, создать 2 Stripe Keypair на две разные валюты и в зависимости от валюты выбранного товара предлагать оплату в соответствующей валюте


Запуск
----
```
apt-get install python3-venv git
git clone https://github.com/Lingors/RishatTest.git
python3 -m venv ./venv
pip3 install -r requirements.txt
python3 manage.py runserver 127.0.0.1:8000
```

Сервис
----------------------------
* `/` - index
* `admin/` - Админка admin.site.urls
* `buy/<item_id>` - купить товар
* `item/<item_id>` - страница товара
* `create_order/` - создать заказ
* `order/<order_id>` - страница заказа
* `buy_order/<order_id>` - купить заказ
