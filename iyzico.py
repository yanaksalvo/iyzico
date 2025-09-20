import aiohttp
import asyncio
import random
from faker import Faker
import json
import urllib.parse
import uuid

# Initialize Faker with Turkish locale
faker = Faker('tr_TR')

# Proxy settings
PROXY_HOST = ""
PROXY_PORT = ""
PROXY_USER = ""
PROXY_PASS = ""
PROXY = None

# Base headers for the requests
BASE_HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'br, gzip, deflate',
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Content-Type': 'application/json',
    'Referer': 'https://www.bursayogamerkezi.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
    'X-Wix-Brand': 'wix',
    'client-binding': 'b46cf57e-47c8-455d-a4ea-0fcccc42e8ab',
    'cookie': 'server-session-bind=b46cf57e-47c8-455d-a4ea-0fcccc42e8ab; XSRF-TOKEN=1757106552|D76Ic3Wo6K2V; hs=2622774; svSession=5e51f97e96c7a53595735b63c134c21c703e0acb46cb2a6589d8a97d09ebaec95adabae6bac4c50c618ab6b93f03d7ca1e60994d53964e647acf431e4f798bcdcaf0411b789eed5721d3deb51d5a53179276f64cee38bd21e6a81567cc3088e8abe280ce32825d0e92204d9d498a9728fa55cd2391d86acd637555f27e6bd2a4b65ccd6faac113e33ef1acaa6c341267; _fbp=fb.1.1757106552368.231527469292405009; bSession=a5918972-6864-4365-acc8-677f8ca72c14|27; ssr-caching=ssr-caching=cache#desc=hit#varnish=hit_hit_etag#dc#desc=fastly_g',
    'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'priority': 'u=1, i',
    'Commonconfig': '%7B%22brand%22%3A%22wix%22%2C%22host%22%3A%22VIEWER%22%2C%22BSI%22%3A%22a5918972-6864-4365-acc8-677f8ca72c14%7C23%22%2C%22siteRevision%22%3A%224%22%2C%22branchId%22%3A%22c1572048-6cc7-470d-96da-0b7bf7f6d982%22%2C%22renderingFlow%22%3A%22NONE%22%2C%22language%22%3A%22tr%22%2C%22locale%22%3A%22tr-tr%22%7D'
}

# User agent rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:109.0) Gecko/20100101 Firefox/120.0"
]

# Lock for sequential processing of requests
request_lock = asyncio.Lock()

def get_random_user_agent():
    """Rastgele bir user agent döndürür."""
    return random.choice(USER_AGENTS)

def generate_random_email():
    """@gmail.com uzantılı rastgele bir e-posta üretir."""
    username = faker.user_name()
    return f"{username}@gmail.com"

def generate_random_phone():
    """5 ile başlayan rastgele bir Türk telefon numarası üretir."""
    return f"5{random.randint(50, 59)}{random.randint(1000000, 9999999)}"

def generate_random_address():
    """Rastgele bir Türk adresi üretir."""
    return {
        "addressLine": faker.street_address(),
        "city": faker.city(),
        "country": "TR",
        "postalCode": faker.postcode(),
        "subdivision": f"TR-{random.randint(1, 81)}"
    }

def get_random_name():
    """Rastgele Türk isim ve soyisim döndürür."""
    return faker.first_name(), faker.last_name()

def generate_device_fingerprint():
    """Rastgele bir device fingerprint üretir."""
    return str(uuid.uuid4()).replace('-', '')

async def get_guest_token():
    """Access-tokens endpoint'inden instance token'ını alır ve çerezleri günceller."""
    headers = BASE_HEADERS.copy()
    headers['User-Agent'] = get_random_user_agent()
    print(f"[BILGI] Gönderilen Header'lar: {json.dumps(headers, indent=2, ensure_ascii=False)}")

    url = "https://www.bursayogamerkezi.com/_api/v1/access-tokens"

    async with request_lock:
        try:
            async with aiohttp.ClientSession() as aio_session:
                async with aio_session.get(url, headers=headers, proxy=PROXY, timeout=20) as response:
                    print(f"[BILGI] Access Tokens İsteği - Durum Kodu: {response.status}")
                    response_text = await response.text()
                    print(f"[HATA AYIKLAMA] Ham Yanıt: {response_text}")
                    if response.status == 200:
                        try:
                            response_data = await response.json()
                            print(f"[HATA AYIKLAMA] Yanıt JSON: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                            access_token = None
                            if 'apps' in response_data:
                                for app_id, app_data in response_data['apps'].items():
                                    int_id = app_data.get('intId')
                                    print(f"[BILGI] intId değeri: {int_id}")
                                    if int_id == 7381:
                                        access_token = app_data.get('instance')
                                        break
                            if access_token:
                                print(f"[BAŞARILI] accessToken alındı: {access_token[:30]}...")
                                set_cookie = response.headers.get('set-cookie')
                                if set_cookie:
                                    new_cookies = []
                                    for cookie in set_cookie.split(','):
                                        cookie = cookie.strip()
                                        if 'hs=' in cookie or 'svSession=' in cookie or 'XSRF-TOKEN=' in cookie or 'server-session-bind=' in cookie or 'bSession=' in cookie:
                                            new_cookies.append(cookie.split(';')[0])
                                    if new_cookies:
                                        BASE_HEADERS['cookie'] = '; '.join(new_cookies + [c for c in BASE_HEADERS['cookie'].split('; ') if not (c.startswith('hs=') or c.startswith('svSession=') or c.startswith('XSRF-TOKEN=') or c.startswith('server-session-bind=') or c.startswith('bSession='))])
                                        print(f"[BILGI] Çerezler güncellendi: {BASE_HEADERS['cookie']}")
                                return access_token, 200
                            else:
                                print(f"[HATA] accessToken veya instance bulunamadı: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                                return None, 500
                        except json.JSONDecodeError as e:
                            print(f"[HATA] Yanıt JSON olarak ayrıştırılamadı: {response_text} | Hata: {e}")
                            return None, 500
                    else:
                        print(f"[HATA] Access tokens isteği başarısız, durum: {response.status} | Yanıt: {response_text}")
                        return None, response.status
        except aiohttp.ClientError as e:
            print(f"[HATA] Access tokens isteği başarısız: {e}")
            return None, 500

async def add_to_cart(auth_token):
    """Sepete ürün ekler."""
    headers = BASE_HEADERS.copy()
    headers['User-Agent'] = get_random_user_agent()
    headers['Authorization'] = f"Bearer {auth_token}"
    headers['X-Wix-Bi-Gateway'] = 'environment=js-sdk,package-name=@wix/auto_sdk_ecom_current-cart,method-fqn=com.wix.ecom.cart.api.v1.CurrentCartService.AddToCurrentCart,entity=wix.ecom.v1.cart'
    print(f"[BILGI] Sepete Ekle Header'ları: {json.dumps(headers, indent=2, ensure_ascii=False)}")

    first_name, last_name = get_random_name()
    full_name = f"{first_name} {last_name}"
    print(f"[BILGI] Rastgele isim kullanılıyor: {full_name}")

    payload = {
        "lineItems": [
            {
                "catalogReference": {
                    "appId": "215238eb-22a5-4c36-9e7b-e7c08025e04e",
                    "catalogItemId": "ae289c47-8b53-97c2-e7ae-72972854745d",
                    "options": {
                        "variantId": "00000000-0000-0000-0000-000000000000",
                        "options": {}
                    }
                },
                "quantity": 1
            }
        ]
    }

    url = "https://www.bursayogamerkezi.com/_api/ecom-cart/v1/carts/current/add-to-cart"

    async with request_lock:
        try:
            async with aiohttp.ClientSession() as aio_session:
                async with aio_session.post(url, headers=headers, json=payload, proxy=PROXY, timeout=20) as response:
                    print(f"[BILGI] Sepete Ekle İsteği - Durum Kodu: {response.status}")
                    response_text = await response.text()
                    print(f"[HATA AYIKLAMA] Sepete Ekle Yanıtı: {response_text}")
                    if response.status == 200:
                        try:
                            response_data = await response.json()
                            print(f"[BAŞARILI] Ürün sepete eklendi. Yanıt: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                            return response_data, 200
                        except json.JSONDecodeError:
                            print(f"[HATA] Yanıt JSON olarak ayrıştırılamadı: {response_text}")
                            return {"hata": "Yanıt JSON olarak ayrıştırılamadı"}, 500
                    else:
                        print(f"[HATA] Sepete ekle isteği başarısız, durum: {response.status} | Yanıt: {response_text}")
                        return {"hata": f"Sepete ekle isteği başarısız, durum: {response.status}"}, response.status
        except aiohttp.ClientError as e:
            print(f"[HATA] Sepete ekle isteği başarısız: {e}")
            return {"hata": f"Sepete ekle isteği başarısız: {e}"}, 500

async def create_checkout(auth_token):
    """Mevcut sepetten ödeme oluşturur."""
    headers = BASE_HEADERS.copy()
    headers['User-Agent'] = get_random_user_agent()
    headers['Authorization'] = f"Bearer {auth_token}"
    headers['X-Wix-Bi-Gateway'] = 'environment=js-sdk,package-name=@wix/auto_sdk_ecom_current-cart,method-fqn=com.wix.ecom.cart.api.v1.CurrentCartService.CreateCheckoutFromCurrentCart,entity=wix.ecom.v1.cart'
    print(f"[BILGI] Ödeme Oluştur Header'ları: {json.dumps(headers, indent=2, ensure_ascii=False)}")

    first_name, last_name = get_random_name()
    full_name = f"{first_name} {last_name}"
    print(f"[BILGI] Rastgele isim kullanılıyor: {full_name}")

    payload = {
        "channelType": "WEB"
    }

    url = "https://www.bursayogamerkezi.com/_api/ecom-cart/v1/carts/current/create-checkout"

    async with request_lock:
        try:
            async with aiohttp.ClientSession() as aio_session:
                async with aio_session.post(url, headers=headers, json=payload, proxy=PROXY, timeout=20) as response:
                    print(f"[BILGI] Ödeme Oluştur İsteği - Durum Kodu: {response.status}")
                    response_text = await response.text()
                    print(f"[HATA AYIKLAMA] Ödeme Oluştur Yanıtı: {response_text}")
                    if response.status == 200:
                        try:
                            response_data = await response.json()
                            print(f"[BAŞARILI] Ödeme oluşturuldu. Yanıt: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                            return response_data, 200
                        except json.JSONDecodeError:
                            print(f"[HATA] Yanıt JSON olarak ayrıştırılamadı: {response_text}")
                            return {"hata": "Yanıt JSON olarak ayrıştırılamadı"}, 500
                    else:
                        print(f"[HATA] Ödeme oluştur isteği başarısız, durum: {response.status} | Yanıt: {response_text}")
                        return {"hata": f"Ödeme oluştur isteği başarısız, durum: {response.status}"}, response.status
        except aiohttp.ClientError as e:
            print(f"[HATA] Ödeme oluştur isteği başarısız: {e}")
            return {"hata": f"Ödeme oluştur isteği başarısız: {e}"}, 500

async def update_checkout(checkout_id, auth_token):
    """Ödemeyi kullanıcı bilgileriyle günceller."""
    headers = BASE_HEADERS.copy()
    headers['User-Agent'] = get_random_user_agent()
    headers['Authorization'] = f"Bearer {auth_token}"
    print(f"[BILGI] Ödeme Güncelle Header'ları: {json.dumps(headers, indent=2, ensure_ascii=False)}")

    first_name, last_name = get_random_name()
    full_name = f"{first_name} {last_name}"
    email = generate_random_email()
    phone = generate_random_phone()
    address = generate_random_address()
    print(f"[BILGI] Rastgele kullanıcı bilgileri: {full_name}, {email}, {phone}, {address['addressLine']}, {address['city']}")

    payload = {
        "operationName": "updateCheckout",
        "query": "mutation updateCheckout($input: EcomCheckoutV1UpdateCheckoutInput!) { updateCheckout(input: $input) { checkout { id } } }",
        "variables": {
            "input": {
                "checkout": {
                    "id": checkout_id,
                    "buyerInfo": {
                        "email": email
                    },
                    "shippingInfo": {
                        "shippingDestination": {
                            "contactDetails": {
                                "firstName": first_name,
                                "lastName": last_name,
                                "phone": phone
                            },
                            "address": {
                                "addressLine": address['addressLine'],
                                "city": address['city'],
                                "country": address['country'],
                                "postalCode": address['postalCode'],
                                "subdivision": address['subdivision']
                            }
                        }
                    }
                },
                "fieldMask": [
                    "shippingInfo.shippingDestination.contactDetails",
                    "buyerInfo.email",
                    "shippingInfo.shippingDestination.addressesServiceId",
                    "shippingInfo.shippingDestination.address"
                ]
            }
        }
    }

    url = "https://www.bursayogamerkezi.com/graphql-server/graphql"

    async with request_lock:
        try:
            async with aiohttp.ClientSession() as aio_session:
                async with aio_session.post(url, headers=headers, json=payload, proxy=PROXY, timeout=20) as response:
                    print(f"[BILGI] Ödeme Güncelle İsteği - Durum Kodu: {response.status}")
                    response_text = await response.text()
                    print(f"[HATA AYIKLAMA] Ödeme Güncelle Yanıtı: {response_text}")
                    if response.status == 200:
                        try:
                            response_data = await response.json()
                            print(f"[BAŞARILI] Ödeme güncellendi. Yanıt: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                            return response_data, 200
                        except json.JSONDecodeError:
                            print(f"[HATA] Yanıt JSON olarak ayrıştırılamadı: {response_text}")
                            return {"hata": "Yanıt JSON olarak ayrıştırılamadı"}, 500
                    else:
                        print(f"[HATA] Ödeme güncelle isteği başarısız, durum: {response.status} | Yanıt: {response_text}")
                        return {"hata": f"Ödeme güncelle isteği başarısız, durum: {response.status}"}, response.status
        except aiohttp.ClientError as e:
            print(f"[HATA] Ödeme güncelle isteği başarısız: {e}")
            return {"hata": f"Ödeme güncelle isteği başarısız: {e}"}, 500

async def get_payment_methods(checkout_id, auth_token, account_ids):
    """Ödeme yöntemlerini alır."""
    headers = BASE_HEADERS.copy()
    headers['User-Agent'] = get_random_user_agent()
    headers['Authorization'] = f"Bearer {auth_token}"
    headers['x-wix-client-artifact-id'] = 'cashier-payments-widget'
    headers['x-xsrf-token'] = BASE_HEADERS['cookie'].split('XSRF-TOKEN=')[1].split(';')[0] if 'XSRF-TOKEN' in BASE_HEADERS['cookie'] else 'missing-token'
    print(f"[BILGI] Ödeme Yöntemleri Header'ları: {json.dumps(headers, indent=2, ensure_ascii=False)}")

    query_params = {
        "returnSavedMethods": "false",
        "merchantInitiated": "false",
        "returnPaymentAgreement": "true",
        "supportSetupFutureUsages": "false",
        "supportDelayedCapture": "false",
        "merchantUseSaveEnabled": "false",
        "allowManualPayment": "true",
        "allowInPersonPayment": "false",
        "country": "TR",
        "amount": "700",
        "locale": "tr",
        "currency": "TRY"
    }

    base_url = f"https://www.bursayogamerkezi.com/_api/payment-services-web/payments/v2/accounts/{account_ids}/payment-methods"
    encoded_params = urllib.parse.urlencode(query_params)
    url = f"{base_url}?{encoded_params}"
    print(f"[BILGI] Ödeme Yöntemleri URL: {url}")

    async with request_lock:
        try:
            async with aiohttp.ClientSession() as aio_session:
                async with aio_session.get(url, headers=headers, proxy=PROXY, timeout=20) as response:
                    print(f"[BILGI] Ödeme Yöntemleri İsteği - Durum Kodu: {response.status}")
                    response_text = await response.text()
                    print(f"[HATA AYIKLAMA] Ödeme Yöntemleri Yanıtı: {response_text}")
                    if response.status == 200:
                        try:
                            response_data = await response.json()
                            print(f"[BAŞARILI] Ödeme yöntemleri alındı. Yanıt: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                            return response_data, 200
                        except json.JSONDecodeError:
                            print(f"[HATA] Yanıt JSON olarak ayrıştırılamadı: {response_text}")
                            return {"hata": "Yanıt JSON olarak ayrıştırılamadı"}, 500
                    else:
                        print(f"[HATA] Ödeme yöntemleri isteği başarısız, durum: {response.status} | Yanıt: {response_text}")
                        return {"hata": f"Ödeme yöntemleri isteği başarısız, durum: {response.status}"}, response.status
        except aiohttp.ClientError as e:
            print(f"[HATA] Ödeme yöntemleri isteği başarısız: {e}")
            return {"hata": f"Ödeme yöntemleri isteği başarısız: {e}"}, 500

async def update_checkout_billing(checkout_id, auth_token):
    """Ödemeyi fatura bilgileriyle günceller."""
    headers = BASE_HEADERS.copy()
    headers['User-Agent'] = get_random_user_agent()
    headers['Authorization'] = f"Bearer {auth_token}"
    print(f"[BILGI] Fatura Bilgileri Güncelle Header'ları: {json.dumps(headers, indent=2, ensure_ascii=False)}")

    payload = {
        "query": """mutation updateCheckout($input: EcomCheckoutV1UpdateCheckoutRequestInput!) {
            checkoutMutation: ecomCheckoutV1UpdateCheckout(input: $input) {
                checkout {
                    ...Checkout
                }
            }
        }

        fragment CatalogReference on ComWixEcommerceCatalogSpiApiV1CatalogReference {
            catalogItemId
            appId
            options
        }

        fragment ProductName on ComWixEcommerceCatalogSpiApiV1ProductName {
            original
            translated
        }

        fragment PageUrlV2 on WixCommonPageUrlV2 {
            relativePath
            url
        }

        fragment MultiCurrencyPrice on ComWixEcommercePlatformCommonApiMultiCurrencyPrice {
            amount
            convertedAmount
            formattedAmount
            formattedConvertedAmount
        }

        fragment TaxRateBreakdown on ComWixEcomTotalsCalculatorV1TaxRateBreakdown {
            name
            rate
            tax {
                ...MultiCurrencyPrice
            }
        }

        fragment ItemTaxFullDetails on ComWixEcomTotalsCalculatorV1ItemTaxFullDetails {
            taxableAmount {
                ...MultiCurrencyPrice
            }
            taxGroupId
            taxRate
            totalTax {
                ...MultiCurrencyPrice
            }
            rateBreakdown {
                ...TaxRateBreakdown
            }
            exemptAmount {
                ...MultiCurrencyPrice
            }
        }

        fragment DescriptionLineName on ComWixEcommerceCatalogSpiApiV1DescriptionLineName {
            original
            translated
        }

        fragment PlainTextValue on ComWixEcommerceCatalogSpiApiV1PlainTextValue {
            original
            translated
        }

        fragment Color on ComWixEcommerceCatalogSpiApiV1Color {
            original
            translated
            code
        }

        fragment DescriptionLine on ComWixEcommerceCatalogSpiApiV1DescriptionLine {
            name {
                ...DescriptionLineName
            }
            lineType
            plainText {
                ...PlainTextValue
            }
            colorInfo {
                ...Color
            }
            plainTextValue {
                ...PlainTextValue
            }
            color
        }

        fragment Image on WixCommonImage {
            id
            url
            height
            width
            altText
            urlExpirationDate
            filename
            sizeInBytes
        }

        fragment ItemAvailabilityInfo on EcomCheckoutV1ItemAvailabilityInfo {
            status
            quantityAvailable
        }

        fragment PhysicalProperties on ComWixEcommerceCatalogSpiApiV1PhysicalProperties {
            weight
            sku
            shippable
        }

        fragment Group on WixCouponsApiV2ScopeGroup {
            name
            entityId
        }

        fragment Scope on WixCouponsApiV2Scope {
            namespace
            group {
                ...Group
            }
        }

        fragment ItemType on ComWixEcommerceCatalogSpiApiV1ItemType {
            preset
            custom
        }

        fragment FreeTrialPeriod on ComWixEcommerceCatalogSpiApiV1FreeTrialPeriod {
            interval
            frequency
        }

        fragment SubscriptionSettings on ComWixEcommerceCatalogSpiApiV1SubscriptionSettings {
            frequency
            interval
            autoRenewal
            billingCycles
            startDate
            freeTrialPeriod {
                ...FreeTrialPeriod
            }
        }

        fragment Title on ComWixEcommerceCatalogSpiApiV1Title {
            original
            translated
        }

        fragment Description on ComWixEcommerceCatalogSpiApiV1Description {
            original
            translated
        }

        fragment SubscriptionOptionInfo on ComWixEcommerceCatalogSpiApiV1SubscriptionOptionInfo {
            subscriptionSettings {
                ...SubscriptionSettings
            }
            title {
                ...Title
            }
            description {
                ...Description
            }
        }

        fragment SecuredMedia on ComWixEcommerceCatalogSpiApiV1SecuredMedia {
            id
            fileName
            fileType
        }

        fragment ServiceProperties on ComWixEcommerceCatalogSpiApiV1ServiceProperties {
            scheduledDate
            numberOfParticipants
        }

        fragment PriceDescription on ComWixEcommerceCatalogSpiApiV1PriceDescription {
            original
            translated
        }

        fragment Policy on ComWixEcommerceCatalogSpiApiV1Policy {
            title
            content
        }

        fragment ModifierGroupName on ComWixEcommercePlatformCommonApiTranslatableString {
            original
            translated
        }

        fragment ModifierLabel on ComWixEcommercePlatformCommonApiTranslatableString {
            original
            translated
        }

        fragment ModifierDetails on ComWixEcommercePlatformCommonApiTranslatableString {
            original
            translated
        }

        fragment Modifier on ComWixEcomCartCheckoutCommonApiV1ItemModifier {
            id
            quantity
            price {
                ...MultiCurrencyPrice
            }
            label {
                ...ModifierLabel
            }
            details {
                ...ModifierDetails
            }
        }

        fragment ModifierGroup on ComWixEcomCartCheckoutCommonApiV1ModifierGroup {
            id
            name {
                ...ModifierGroupName
            }
            modifiers {
                ...Modifier
            }
        }

        fragment LineItem on EcomCheckoutV1LineItem {
            id
            quantity
            catalogReference {
                ...CatalogReference
            }
            productName {
                ...ProductName
            }
            url {
                ...PageUrlV2
            }
            price {
                ...MultiCurrencyPrice
            }
            lineItemPrice {
                ...MultiCurrencyPrice
            }
            fullPrice {
                ...MultiCurrencyPrice
            }
            priceBeforeDiscounts {
                ...MultiCurrencyPrice
            }
            totalPriceAfterTax {
                ...MultiCurrencyPrice
            }
            totalPriceBeforeTax {
                ...MultiCurrencyPrice
            }
            modifiersTotalPrice {
                ...MultiCurrencyPrice
            }
            taxDetails {
                ...ItemTaxFullDetails
            }
            discount {
                ...MultiCurrencyPrice
            }
            descriptionLines {
                ...DescriptionLine
            }
            media {
                ...Image
            }
            availability {
                ...ItemAvailabilityInfo
            }
            physicalProperties {
                ...PhysicalProperties
            }
            couponScopes {
                ...Scope
            }
            itemType {
                ...ItemType
            }
            subscriptionOptionInfo {
                ...SubscriptionOptionInfo
            }
            fulfillerId
            shippingGroupId
            digitalFile {
                ...SecuredMedia
            }
            paymentOption
            serviceProperties {
                ...ServiceProperties
            }
            rootCatalogItemId
            priceDescription {
                ...PriceDescription
            }
            depositAmount {
                ...MultiCurrencyPrice
            }
            policies {
                ...Policy
            }
            consentRequiredPaymentPolicy
            savePaymentMethod
            priceUndetermined
            fixedQuantity
            membersOnly
            deliveryProfileId
            modifierGroups {
                ...ModifierGroup
            }
        }

        fragment StreetAddress on WixCommonStreetAddress {
            number
            name
            apt
            formattedAddressLine
        }

        fragment ApiAddressNoGeo on ComWixEcommercePlatformCommonApiAddress {
            country
            subdivision
            city
            postalCode
            addressLine
            addressLine2
            countryFullname
            subdivisionFullname
            streetAddress {
                ...StreetAddress
            }
        }

        fragment VatId on WixCommonVatId {
            id
            type
        }

        fragment FullAddressContactDetails on ComWixEcommercePlatformCommonApiFullAddressContactDetails {
            firstName
            lastName
            phone
            company
            vatId {
                ...VatId
            }
        }

        fragment AddressWithContactNoGeo on EcomCheckoutV1AddressWithContact {
            address {
                ...ApiAddressNoGeo
            }
            contactDetails {
                ...FullAddressContactDetails
            }
            addressesServiceId
        }

        fragment GeoCode on WixCommonAddressLocation {
            latitude
            longitude
        }

        fragment ApiAddress on ComWixEcommercePlatformCommonApiAddress {
            ...ApiAddressNoGeo
            geocode {
                ...GeoCode
            }
        }

        fragment AddressWithContact on EcomCheckoutV1AddressWithContact {
            address {
                ...ApiAddress
            }
            contactDetails {
                ...FullAddressContactDetails
            }
            addressesServiceId
        }

        fragment PickupDetails on ComWixEcomTotalsCalculatorV1PickupDetails {
            address {
                ...ApiAddress
            }
            businessLocation
            pickupMethod
        }

        fragment DeliveryLogistics on ComWixEcomTotalsCalculatorV1DeliveryLogistics {
            deliveryTime
            instructions
            pickupDetails {
                ...PickupDetails
            }
            deliveryTimeSlot {
                from
                to
            }
        }

        fragment SelectedCarrierServiceOptionPrices on ComWixEcomTotalsCalculatorV1SelectedCarrierServiceOptionPrices {
            totalPriceAfterTax {
                ...MultiCurrencyPrice
            }
            totalPriceBeforeTax {
                ...MultiCurrencyPrice
            }
            taxDetails {
                ...ItemTaxFullDetails
            }
            totalDiscount {
                ...MultiCurrencyPrice
            }
            price {
                ...MultiCurrencyPrice
            }
        }

        fragment SelectedCarrierServiceOptionOtherCharge on ComWixEcomTotalsCalculatorV1SelectedCarrierServiceOptionOtherCharge {
            type
            details
            cost {
                ...SelectedCarrierServiceOptionPrices
            }
        }

        fragment SelectedCarrierServiceOption on ComWixEcomTotalsCalculatorV1SelectedCarrierServiceOption {
            code
            title
            logistics {
                ...DeliveryLogistics
            }
            cost {
                ...SelectedCarrierServiceOptionPrices
            }
            requestedShippingOption
            otherCharges {
                ...SelectedCarrierServiceOptionOtherCharge
            }
            carrierId
        }

        fragment ShippingRegion on ComWixEcomTotalsCalculatorV1ShippingRegion {
            id
            name
        }

        fragment OtherCharge on ComWixEcomTotalsCalculatorV1OtherCharge {
            type
            price {
                ...MultiCurrencyPrice
            }
        }

        fragment ShippingPrice on ComWixEcomTotalsCalculatorV1ShippingPrice {
            price {
                ...MultiCurrencyPrice
            }
            otherCharges {
                ...OtherCharge
            }
        }

        fragment ShippingOption on ComWixEcomTotalsCalculatorV1ShippingOption {
            code
            title
            partial
            logistics {
                ...DeliveryLogistics
            }
            cost {
                ...ShippingPrice
            }
        }

        fragment CarrierServiceOption on ComWixEcomTotalsCalculatorV1CarrierServiceOption {
            carrierId
            shippingOptions {
                ...ShippingOption
            }
        }

        fragment ShippingInfo on EcomCheckoutV1ShippingInfo {
            shippingDestination {
                ...AddressWithContact
            }
            selectedCarrierServiceOption {
                ...SelectedCarrierServiceOption
            }
            region {
                ...ShippingRegion
            }
            carrierServiceOptions {
                ...CarrierServiceOption
            }
        }

        fragment BuyerInfo on EcomCheckoutV1BuyerInfo {
            contactId
            email
            visitorId
            memberId
            openAccess
        }

        fragment PriceSummary on ComWixEcomTotalsCalculatorV1PriceSummary {
            subtotal {
                ...MultiCurrencyPrice
            }
            shipping {
                ...MultiCurrencyPrice
            }
            tax {
                ...MultiCurrencyPrice
            }
            discount {
                ...MultiCurrencyPrice
            }
            total {
                ...MultiCurrencyPrice
            }
            additionalFees {
                ...MultiCurrencyPrice
            }
        }

        fragment ApplicationError on WixApiApplicationError {
            code
            description
            data
        }

        fragment FieldViolation on WixApiValidationErrorFieldViolation {
            field
            description
            violatedRule
            ruleName
            data
        }

        fragment ValidationError on WixApiValidationError {
            fieldViolations {
                ...FieldViolation
            }
        }

        fragment ErrorDetails on WixApiDetails {
            applicationError {
                ...ApplicationError
            }
            validationError {
                ...ValidationError
            }
            tracing
        }

        fragment CarrierError on ComWixEcomTotalsCalculatorV1CarrierError {
            carrierId
            error {
                ...ErrorDetails
            }
        }

        fragment CarrierErrors on ComWixEcomTotalsCalculatorV1CarrierErrors {
            errors {
                ...CarrierError
            }
        }

        fragment CalculationErrors on ComWixEcomTotalsCalculatorV1CalculationErrors {
            generalShippingCalculationError {
                ...ErrorDetails
            }
            carrierErrors {
                ...CarrierErrors
            }
            taxCalculationError {
                ...ErrorDetails
            }
            couponCalculationError {
                ...ErrorDetails
            }
            giftCardCalculationError {
                ...ErrorDetails
            }
            membershipError {
                ...ErrorDetails
            }
            discountsCalculationError {
                ...ErrorDetails
            }
            orderValidationErrors {
                ...ApplicationError
            }
        }

        fragment GiftCard on ComWixEcomTotalsCalculatorV1GiftCard {
            id
            obfuscatedCode
            amount {
                ...MultiCurrencyPrice
            }
            appId
        }

        fragment Coupon on ComWixEcomTotalsCalculatorV1Coupon {
            id
            code
            amount {
                ...MultiCurrencyPrice
            }
            name
            couponType
        }

        fragment MerchantDiscount on ComWixEcomTotalsCalculatorV1MerchantDiscount {
            amount {
                ...MultiCurrencyPrice
            }
        }

        fragment DiscountRuleName on ComWixEcomTotalsCalculatorV1DiscountRuleName {
            original
            translated
        }

        fragment DiscountRule on ComWixEcomTotalsCalculatorV1DiscountRule {
            id
            name {
                ...DiscountRuleName
            }
            amount {
                ...MultiCurrencyPrice
            }
        }

        fragment AppliedDiscount on ComWixEcomTotalsCalculatorV1AppliedDiscount {
            discountType
            lineItemIds
            coupon {
                ...Coupon
            }
            merchantDiscount {
                ...MerchantDiscount
            }
            discountRule {
                ...DiscountRule
            }
        }

        fragment CustomField on ComWixEcomOrdersV1CustomField {
            value
            title
            translatedTitle
        }

        fragment AutoTaxFallbackCalculationDetails on ComWixEcomTaxApiAutoTaxFallbackCalculationDetails {
            fallbackReason
            error {
                ...ApplicationError
            }
        }

        fragment TaxCalculationDetails on ComWixEcomTaxApiTaxCalculationDetails {
            rateType
            manualRateReason
            autoTaxFallbackDetails {
                ...AutoTaxFallbackCalculationDetails
            }
        }

        fragment AggregatedTaxBreakdown on ComWixEcomTotalsCalculatorV1AggregatedTaxBreakdown {
            taxName
            aggregatedTaxAmount {
                ...MultiCurrencyPrice
            }
        }

        fragment TaxSummary on ComWixEcomTotalsCalculatorV1TaxSummary {
            taxableAmount {
                ...MultiCurrencyPrice
            }
            totalTax {
                ...MultiCurrencyPrice
            }
            manualTaxRate
            calculationDetails {
                ...TaxCalculationDetails
            }
            taxEstimationId
            averageTaxRate
            totalExempt {
                ...MultiCurrencyPrice
            }
            aggregatedTaxBreakdown {
                ...AggregatedTaxBreakdown
            }
        }

        fragment CreatedBy on EcomCheckoutV1CreatedBy {
            userId
            memberId
            visitorId
            appId
        }

        fragment MembershipName on ComWixEcomMembershipsSpiV1MembershipName {
            original
            translated
        }

        fragment MembershipPaymentCredits on ComWixEcomMembershipsSpiV1MembershipPaymentCredits {
            total
            remaining
        }

        fragment Membership on ComWixEcomMembershipsSpiV1HostMembership {
            id
            appId
            name {
                ...MembershipName
            }
            lineItemIds
            credits {
                ...MembershipPaymentCredits
            }
            expirationDate
            additionalData
        }

        fragment InvalidMembership on ComWixEcomMembershipsSpiV1HostInvalidMembership {
            membership {
                ...Membership
            }
            reason
        }

        fragment SelectedMembership on ComWixEcomMembershipsSpiV1HostSelectedMembership {
            id
            appId
            lineItemIds
        }

        fragment MembershipOptions on EcomCheckoutV1MembershipOptions {
            eligibleMemberships {
                ...Membership
            }
            invalidMemberships {
                ...InvalidMembership
            }
            selectedMemberships {
                memberships {
                    ...SelectedMembership
                }
            }
        }

        fragment AdditionalFee on ComWixEcomTotalsCalculatorV1AdditionalFee {
            code
            name
            translatedName
            price {
                ...MultiCurrencyPrice
            }
            taxDetails {
                ...ItemTaxFullDetails
            }
            providerAppId
            priceBeforeTax {
                ...MultiCurrencyPrice
            }
        }

        fragment ConversionInfo on EcomCheckoutV1ConversionInfo {
            siteCurrency
            conversionRate
        }

        fragment RenderingConfig on ComWixEcomLineItemsEnricherSpiApiV1LineItemRenderingConfig {
            hidePrice
            hideQuantity
        }

        fragment EnrichedLineItem on ComWixEcomLineItemsEnricherSpiApiV1EnrichedLineItem {
            id
            overriddenDescriptionLines {
                descriptionLines {
                    ...DescriptionLine
                }
            }
            renderingConfig {
                ...RenderingConfig
            }
        }

        fragment ViolationLineItemTarget on ComWixEcommerceValidationsSpiV1TargetLineItem {
            id
            name
            suggestedFix
        }

        fragment ViolationOtherTarget on ComWixEcommerceValidationsSpiV1TargetOther {
            name
        }

        fragment ViolationTarget on ComWixEcommerceValidationsSpiV1Target {
            lineItem {
                ...ViolationLineItemTarget
            }
            other {
                ...ViolationOtherTarget
            }
        }

        fragment Violation on ComWixEcommerceValidationsSpiV1Violation {
            severity
            target {
                ...ViolationTarget
            }
            description
        }

        fragment ExtendedFields on WixCommonDataDataextensionsExtendedFields {
            namespaces
        }

        fragment CustomSettings on EcomCheckoutV1CustomSettings {
            lockGiftCard
            lockCouponCode
            disabledManualPayment
            disabledPolicyAgreementCheckbox
        }

        fragment SubscriptionCharge on EcomCheckoutV1Charge {
            cycleBillingDate
            cycleCount
            cycleFrom
            priceSummary {
                ...PriceSummary
            }
        }

        fragment SubscriptionCharges on EcomCheckoutV1SubscriptionCharges {
            charges {
                ...SubscriptionCharge
            }
            description
            lineItemIds
        }

        fragment Checkout on EcomCheckoutV1Checkout {
            id
            lineItems {
                ...LineItem
            }
            billingInfo {
                ...AddressWithContactNoGeo
            }
            shippingInfo {
                ...ShippingInfo
            }
            buyerNote
            buyerInfo {
                ...BuyerInfo
            }
            conversionCurrency
            priceSummary {
                ...PriceSummary
            }
            calculationErrors {
                ...CalculationErrors
            }
            giftCard {
                ...GiftCard
            }
            appliedDiscounts {
                ...AppliedDiscount
            }
            customFields {
                ...CustomField
            }
            weightUnit
            taxSummary {
                ...TaxSummary
            }
            currency
            paymentCurrency
            channelType
            siteLanguage
            buyerLanguage
            completed
            taxIncludedInPrice
            createdBy {
                ...CreatedBy
            }
            createdDate
            updatedDate
            payNow {
                ...PriceSummary
            }
            payLater {
                ...PriceSummary
            }
            payAfterFreeTrial {
                ...PriceSummary
            }
            membershipOptions {
                ...MembershipOptions
            }
            additionalFees {
                ...AdditionalFee
            }
            cartId
            conversionInfo {
                ...ConversionInfo
            }
            payNowTotalAfterGiftCard {
                ...MultiCurrencyPrice
            }
            purchaseFlowId
            calculationErrors {
                ...CalculationErrors
            }
            externalEnrichedLineItems {
                enrichedLineItems {
                    ...EnrichedLineItem
                }
            }
            violations {
                ...Violation
            }
            totalAfterGiftCard {
                ...MultiCurrencyPrice
            }
            extendedFields {
                ...ExtendedFields
            }
            customSettings {
                ...CustomSettings
            }
            subscriptionCharges {
                ...SubscriptionCharges
            }
            paymentRequired
            taxIncludedInPrice
            lineItemsSubtotal {
                ...MultiCurrencyPrice
            }
        }""",
        "variables": {
            "input": {
                "checkout": {
                    "id": checkout_id,
                    "billingInfo": {
                        "contactDetails": {
                            "firstName": "Yunus",
                            "lastName": "Balık",
                            "phone": "5364587690"
                        },
                        "address": {
                            "country": "TR",
                            "city": "Bozova",
                            "subdivision": "TR-63",
                            "postalCode": "63853",
                            "addressLine": "Yunus Caddesi"
                        }
                    }
                },
                "fieldMask": [
                    "billingInfo.contactDetails",
                    "billingInfo.address"
                ]
            }
        },
        "operationName": "updateCheckout"
    }

    url = "https://www.bursayogamerkezi.com/graphql-server/graphql"

    async with request_lock:
        try:
            async with aiohttp.ClientSession() as aio_session:
                async with aio_session.post(url, headers=headers, json=payload, proxy=PROXY, timeout=20) as response:
                    print(f"[BILGI] Fatura Bilgileri Güncelle İsteği - Durum Kodu: {response.status}")
                    response_text = await response.text()
                    print(f"[HATA AYIKLAMA] Fatura Bilgileri Güncelle Yanıtı: {response_text}")
                    if response.status == 200:
                        try:
                            response_data = await response.json()
                            print(f"[BAŞARILI] Fatura bilgileri güncellendi. Yanıt: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                            return response_data, 200
                        except json.JSONDecodeError:
                            print(f"[HATA] Yanıt JSON olarak ayrıştırılamadı: {response_text}")
                            return {"hata": "Yanıt JSON olarak ayrıştırılamadı"}, 500
                    else:
                        print(f"[HATA] Fatura bilgileri güncelle isteği başarısız, durum: {response.status} | Yanıt: {response_text}")
                        return {"hata": f"Fatura bilgileri güncelle isteği başarısız, durum: {response.status}"}, response.status
        except aiohttp.ClientError as e:
            print(f"[HATA] Fatura bilgileri güncelle isteği başarısız: {e}")
            return {"hata": f"Fatura bilgileri güncelle isteği başarısız: {e}"}, 500

async def submit_payment_details(checkout_id, auth_token, buyer_id):
    """Ödeme detaylarını gönderir."""
    headers = BASE_HEADERS.copy()
    headers['User-Agent'] = get_random_user_agent()
    headers['Authorization'] = f"Bearer {auth_token}"
    headers['x-wix-client-artifact-id'] = 'cashier-payments-widget'
    headers['x-xsrf-token'] = BASE_HEADERS['cookie'].split('XSRF-TOKEN=')[1].split(';')[0] if 'XSRF-TOKEN' in BASE_HEADERS['cookie'] else 'missing-token'
    print(f"[BILGI] Ödeme Detayları Gönder Header'ları: {json.dumps(headers, indent=2, ensure_ascii=False)}")

    payload = {
        "details": {
            "paymentMethod": "iyzico",
            "billingAddress": {
                "zipCode": "63853",
                "city": "Bozova",
                "address": "Yunus Caddesi",
                "countryCode": "TUR",
                "email": generate_random_email(),
                "firstName": "Yunus",
                "lastName": "Balık"
            },
            "redirectTarget": "SAME_WINDOW",
            "buyerInfo": {
                "buyerId": buyer_id or str(uuid.uuid4()),
                "buyerLanguage": "tr"
            },
            "clientInfo": {
                "deviceFingerprint": generate_device_fingerprint()
            }
        }
    }

    url = "https://www.bursayogamerkezi.com/_api/payment-services-web/payments/v2/payment-details"

    async with request_lock:
        try:
            async with aiohttp.ClientSession() as aio_session:
                async with aio_session.post(url, headers=headers, json=payload, proxy=PROXY, timeout=20) as response:
                    print(f"[BILGI] Ödeme Detayları Gönder İsteği - Durum Kodu: {response.status}")
                    response_text = await response.text()
                    print(f"[HATA AYIKLAMA] Ödeme Detayları Gönder Yanıtı: {response_text}")
                    if response.status == 200:
                        try:
                            response_data = await response.json()
                            print(f"[BAŞARILI] Ödeme detayları gönderildi. Yanıt: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                            return response_data, 200
                        except json.JSONDecodeError:
                            print(f"[HATA] Yanıt JSON olarak ayrıştırılamadı: {response_text}")
                            return {"hata": "Yanıt JSON olarak ayrıştırılamadı"}, 500
                    else:
                        print(f"[HATA] Ödeme detayları gönder isteği başarısız, durum: {response.status} | Yanıt: {response_text}")
                        return {"hata": f"Ödeme detayları gönder isteği başarısız, durum: {response.status}"}, response.status
        except aiohttp.ClientError as e:
            print(f"[HATA] Ödeme detayları gönder isteği başarısız: {e}")
            return {"hata": f"Ödeme detayları gönder isteği başarısız: {e}"}, 500

async def create_order_and_charge(checkout_id, auth_token, payment_token):
    """Sipariş oluşturur ve ödeme işlemini başlatır."""
    headers = BASE_HEADERS.copy()
    headers['User-Agent'] = get_random_user_agent()
    headers['Authorization'] = f"Bearer {auth_token}"
    headers['x-wix-client-artifact-id'] = 'cashier-payments-widget'
    headers['x-xsrf-token'] = BASE_HEADERS['cookie'].split('XSRF-TOKEN=')[1].split(';')[0] if 'XSRF-TOKEN' in BASE_HEADERS['cookie'] else 'missing-token'
    print(f"[BILGI] Sipariş Oluştur ve Ödeme Başlat Header'ları: {json.dumps(headers, indent=2, ensure_ascii=False)}")

    payload = {
        "query": "mutation createOrderAndCharge($input: EcomCheckoutV1CreateOrderAndChargeRequestInput!) {\n  checkoutMutation: ecomCheckoutV1CreateOrderAndCharge(input: $input) {\n    orderId\n    subscriptionId\n    paymentResponseToken\n    paymentGatewayOrderId\n    checkoutCompleted\n  }\n}",
        "variables": {
            "input": {
                "id": checkout_id,
                "paymentToken": payment_token,
                "savePaymentMethod": False,
                "delayCapture": False,
                "urlParams": {
                    "errorUrl": f"https://www.bursayogamerkezi.com/checkout?checkoutId={checkout_id}&origin=shopping+cart&redirect=error",
                    "cancelUrl": f"https://www.bursayogamerkezi.com/checkout?checkoutId={checkout_id}&origin=shopping+cart&redirect=cancel",
                    "successUrl": "https://www.bursayogamerkezi.com/thank-you-page/{orderId}?appSectionParams=%7B%22objectType%22%3A%22order%22%2C%22origin%22%3A%22checkout%22%7D",
                    "pendingUrl": "https://www.bursayogamerkezi.com/thank-you-page/{orderId}?appSectionParams=%7B%22objectType%22%3A%22order%22%2C%22origin%22%3A%22checkout%22%7D"
                }
            }
        },
        "operationName": "createOrderAndCharge"
    }

    url = "https://www.bursayogamerkezi.com/graphql-server/graphql"

    async with request_lock:
        try:
            async with aiohttp.ClientSession() as aio_session:
                async with aio_session.post(url, headers=headers, json=payload, proxy=PROXY, timeout=20) as response:
                    print(f"[BILGI] Sipariş Oluştur ve Ödeme Başlat İsteği - Durum Kodu: {response.status}")
                    response_text = await response.text()
                    print(f"[HATA AYIKLAMA] Sipariş Oluştur ve Ödeme Başlat Yanıtı: {response_text}")
                    if response.status == 200:
                        try:
                            response_data = await response.json()
                            print(f"[BAŞARILI] Sipariş oluşturuldu ve ödeme başlatıldı. Yanıt: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                            return response_data, 200
                        except json.JSONDecodeError:
                            print(f"[HATA] Yanıt JSON olarak ayrıştırılamadı: {response_text}")
                            return {"hata": "Yanıt JSON olarak ayrıştırılamadı"}, 500
                    else:
                        print(f"[HATA] Sipariş oluştur ve ödeme başlat isteği başarısız, durum: {response.status} | Yanıt: {response_text}")
                        return {"hata": f"Sipariş oluştur ve ödeme başlat isteği başarısız, durum: {response.status}"}, response.status
        except aiohttp.ClientError as e:
            print(f"[HATA] Sipariş oluştur ve ödeme başlat isteği başarısız: {e}")
            return {"hata": f"Sipariş oluştur ve ödeme başlat isteği başarısız: {e}"}, 500

async def finalize_payment(checkout_id, auth_token, payment_details_response):
    """Ödeme işlemini tamamlamak için frog.wix.com'a istek gönderir ve yönlendirmeleri takip eder."""
    headers = BASE_HEADERS.copy()
    headers['User-Agent'] = get_random_user_agent()
    headers['Authorization'] = f"Bearer {auth_token}"
    headers['x-wix-client-artifact-id'] = 'cashier-payments-widget'
    headers['x-xsrf-token'] = BASE_HEADERS['cookie'].split('XSRF-TOKEN=')[1].split(';')[0] if 'XSRF-TOKEN' in BASE_HEADERS['cookie'] else 'missing-token'
    print(f"[BILGI] Ödeme Tamamlama Header'ları: {json.dumps(headers, indent=2, ensure_ascii=False)}")

    # Query parametreleri
    query_params = {
        "appId": "1380b703-ce81-ff05-f115-39571d94dfcd",
        "appInstanceId": "6dfdca88-67d6-48e4-b6f4-60bb9094221c",
        "mobileAppId": "undefined",
        "mobileAppVersion": "undefined",
        "visitorId": payment_details_response.get('visitorId', str(uuid.uuid4())),
        "orderSnapshotId": "undefined",
        "msid": payment_details_response.get('metaSiteId', '0f542113-d033-4eeb-90a8-9249c8bb6a01'),
        "checkoutSessionId": payment_details_response.get('detailsId', str(uuid.uuid4())),
        "appSessionId": "undefined",
        "pageType": "payment_component",
        "merchantInitiated": "undefined",
        "siteCurrency": "TRY",
        "_brandId": "wix",
        "_siteBranchId": "c1572048-6cc7-470d-96da-0b7bf7f6d982",
        "_ms": "70537",
        "_isHeadless": "undefined",
        "_hostingPlatform": "VIEWER",
        "_lv": "2.0.985|C",
        "src": "64",
        "evid": "180",
        "amount": "70000000",
        "currency": "TRY",
        "savePaymentMethodDisplayOption": "SHOW_NOTHING",
        "allowMerchantUseDisplayOption": "SHOW_NOTHING",
        "delayedCapture": "false",
        "setupFutureUsages": "false",
        "purchaseFlowId": payment_details_response.get('purchaseFlowId', str(uuid.uuid4())),
        "catalogAppId": "215238eb-22a5-4c36-9e7b-e7c08025e04e",
        "paymentCategory": "iyzico",
        "paymentProvider": "f748e7fb-1694-42b9-afec-19e27c62f32b",
        "payWith": "iyzico",
        "passedMandatoryFields": "countryCode,state,holderId,email,firstName,lastName,street,houseNumber,address,city,zipCode,phone",
        "requiredPmMandatoryFields": "zipCode,city,address,countryCode,email,firstName,lastName",
        "_isca": "1",
        "_iscf": "1",
        "_ispd": "0",
        "_ise": "0",
        "_": "175715375590917"
    }

    encoded_params = urllib.parse.urlencode(query_params)
    url = f"https://frog.wix.com/?{encoded_params}"
    print(f"[BILGI] Ödeme Tamamlama URL: {url}")

    async with request_lock:
        try:
            async with aiohttp.ClientSession() as aio_session:
                async with aio_session.get(url, headers=headers, proxy=PROXY, timeout=20, allow_redirects=True) as response:
                    print(f"[BILGI] Ödeme Tamamlama İsteği - Durum Kodu: {response.status}")
                    content_type = response.headers.get('Content-Type', '')
                    print(f"[BILGI] Content-Type: {content_type}")

                    # Yanıtı ham bayt olarak oku
                    response_body = await response.read()
                    print(f"[HATA AYIKLAMA] Ham Yanıt Uzunluğu: {len(response_body)} bayt")

                    if response.status == 204:
                        # 204 durumunda yönlendirme kontrolü
                        redirect_url = response.headers.get('Location')
                        if redirect_url:
                            print(f"[BILGI] Yönlendirme tespit edildi: {redirect_url}")
                            async with aio_session.get(redirect_url, headers=headers, proxy=PROXY, timeout=20) as redirect_response:
                                print(f"[BILGI] Yönlendirme İsteği - Durum Kodu: {redirect_response.status}")
                                redirect_content_type = redirect_response.headers.get('Content-Type', '')
                                print(f"[BILGI] Yönlendirme Content-Type: {redirect_content_type}")
                                redirect_body = await redirect_response.read()
                                print(f"[HATA AYIKLAMA] Yönlendirme Yanıt Uzunluğu: {len(redirect_body)} bayt")
                                if redirect_response.status == 200:
                                    if 'application/json' in redirect_content_type:
                                        try:
                                            redirect_data = json.loads(redirect_body.decode('utf-8'))
                                            print(f"[BAŞARILI] Yönlendirme başarılı. Yanıt: {json.dumps(redirect_data, indent=2, ensure_ascii=False)}")
                                            return redirect_data, 200
                                        except json.JSONDecodeError:
                                            print(f"[HATA] Yönlendirme yanıtı JSON olarak ayrıştırılamadı")
                                            return {"hata": "Yönlendirme yanıtı JSON olarak ayrıştırılamadı", "redirect_url": redirect_url}, 500
                                    else:
                                        # HTML veya başka bir format, içeriği logla
                                        try:
                                            redirect_text = redirect_body.decode('utf-8', errors='ignore')
                                            print(f"[HATA AYIKLAMA] Yönlendirme Yanıtı (UTF-8 ile zorlanmış): {redirect_text[:1000]}...")
                                            return {"mesaj": "Yönlendirme yanıtı metin tabanlı, ancak JSON değil", "redirect_url": redirect_url, "content": redirect_text[:1000]}, 200
                                        except UnicodeDecodeError:
                                            print(f"[HATA] Yönlendirme yanıtı metne çevrilemedi")
                                            return {"hata": "Yönlendirme yanıtı metne çevrilemedi", "redirect_url": redirect_url}, 500
                                else:
                                    print(f"[HATA] Yönlendirme isteği başarısız, durum: {redirect_response.status}")
                                    return {"hata": f"Yönlendirme isteği başarısız, durum: {redirect_response.status}", "redirect_url": redirect_url}, redirect_response.status
                        else:
                            print(f"[BILGI] 204 yanıtı alındı, yönlendirme bulunamadı")
                            return {"mesaj": "204 yanıtı alındı, yönlendirme yok"}, 204
                    elif response.status == 200:
                        # 200 durumunda yanıt türünü kontrol et
                        if 'application/json' in content_type:
                            try:
                                response_data = json.loads(response_body.decode('utf-8'))
                                print(f"[BAŞARILI] Ödeme tamamlama başarılı. Yanıt: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                                return response_data, 200
                            except json.JSONDecodeError:
                                print(f"[HATA] Yanıt JSON olarak ayrıştırılamadı")
                                return {"hata": "Yanıt JSON olarak ayrıştırılamadı", "content_type": content_type}, 500
                        elif 'text/html' in content_type or 'text' in content_type:
                            # HTML veya metin tabanlı yanıt
                            try:
                                response_text = response_body.decode('utf-8', errors='ignore')
                                print(f"[HATA AYIKLAMA] Yanıt (UTF-8 ile zorlanmış): {response_text[:1000]}...")
                                # HTML içinde meta yenileme veya JS yönlendirme kontrolü
                                import re
                                meta_refresh = re.search(r'<meta[^>]+refresh[^>]+url=([\'"])?(.*?)[\1>]', response_text, re.IGNORECASE)
                                if meta_refresh:
                                    redirect_url = meta_refresh.group(2)
                                    print(f"[BILGI] HTML meta yenileme tespit edildi: {redirect_url}")
                                    async with aio_session.get(redirect_url, headers=headers, proxy=PROXY, timeout=20) as redirect_response:
                                        redirect_body = await redirect_response.read()
                                        print(f"[BILGI] Meta Yönlendirme İsteği - Durum Kodu: {redirect_response.status}")
                                        redirect_content_type = redirect_response.headers.get('Content-Type', '')
                                        print(f"[BILGI] Meta Yönlendirme Content-Type: {redirect_content_type}")
                                        if redirect_response.status == 200 and 'application/json' in redirect_content_type:
                                            try:
                                                redirect_data = json.loads(redirect_body.decode('utf-8'))
                                                print(f"[BAŞARILI] Meta yönlendirme başarılı. Yanıt: {json.dumps(redirect_data, indent=2, ensure_ascii=False)}")
                                                return redirect_data, 200
                                            except json.JSONDecodeError:
                                                print(f"[HATA] Meta yönlendirme yanıtı JSON olarak ayrıştırılamadı")
                                                return {"hata": "Meta yönlendirme yanıtı JSON olarak ayrıştırılamadı", "redirect_url": redirect_url}, 500
                                        else:
                                            try:
                                                redirect_text = redirect_body.decode('utf-8', errors='ignore')
                                                print(f"[HATA AYIKLAMA] Meta Yönlendirme Yanıtı: {redirect_text[:1000]}...")
                                                return {"mesaj": "Meta yönlendirme yanıtı metin tabanlı", "redirect_url": redirect_url, "content": redirect_text[:1000]}, redirect_response.status
                                            except UnicodeDecodeError:
                                                print(f"[HATA] Meta yönlendirme yanıtı metne çevrilemedi")
                                                return {"hata": "Meta yönlendirme yanıtı metne çevrilemedi", "redirect_url": redirect_url}, 500
                                else:
                                    print(f"[BILGI] HTML yanıtı alındı, meta yenileme bulunamadı")
                                    return {"mesaj": "HTML yanıtı alındı, yönlendirme yok", "content": response_text[:1000]}, 200
                            except UnicodeDecodeError:
                                print(f"[HATA] Yanıt metne çevrilemedi")
                                return {"hata": "Yanıt metne çevrilemedi", "content_type": content_type}, 500
                        else:
                            # Diğer içerik türleri (binary, vb.)
                            print(f"[HATA] Yanıt metin tabanlı değil, Content-Type: {content_type}")
                            return {"hata": "Yanıt metin tabanlı değil", "content_type": content_type, "content_length": len(response_body)}, 500
                    else:
                        print(f"[HATA] Ödeme tamamlama isteği başarısız, durum: {response.status}")
                        return {"hata": f"Ödeme tamamlama isteği başarısız, durum: {response.status}", "content_type": content_type}, response.status
        except aiohttp.ClientError as e:
            print(f"[HATA] Ödeme tamamlama isteği başarısız: {e}")
            return {"hata": f"Ödeme tamamlama isteği başarısız: {e}"}, 500

async def full_process():
    """Tam süreci yürüt: token al, sepete ekle, ödeme oluştur, ödemeyi güncelle, fatura bilgilerini güncelle, ödeme detaylarını gönder, sipariş oluştur ve ödeme başlat, ödeme tamamla."""
    print("[BILGI] Süreç başladı...")
    auth_token, auth_status = await get_guest_token()
    if auth_status != 200 or not auth_token:
        print(f"[HATA] accessToken alınamadı, durum: {auth_status}")
        return {"hata": "accessToken alınamadı"}, auth_status

    add_to_cart_response, add_to_cart_status = await add_to_cart(auth_token)
    if add_to_cart_status != 200:
        print(f"[HATA] Sepete ekleme başarısız, durum: {add_to_cart_status}")
        return add_to_cart_response, add_to_cart_status

    create_checkout_response, create_checkout_status = await create_checkout(auth_token)
    if create_checkout_status != 200:
        print(f"[HATA] Ödeme oluşturma başarısız, durum: {create_checkout_status}")
        return create_checkout_response, create_checkout_status

    checkout_id = create_checkout_response.get('checkoutId')
    if not checkout_id:
        print(f"[HATA] Ödeme ID'si yanıtta bulunamadı")
        return {"hata": "Ödeme ID'si yanıtta bulunamadı"}, 500

    update_checkout_response, update_checkout_status = await update_checkout(checkout_id, auth_token)
    if update_checkout_status != 200:
        print(f"[HATA] Ödeme güncelleme başarısız, durum: {update_checkout_status}")
        return update_checkout_response, update_checkout_status

    account_ids = create_checkout_response.get('appDefId', '') + ':' + create_checkout_response.get('instanceId', '')
    if not account_ids or account_ids == ':':
        account_ids = "1380b703-ce81-ff05-f115-39571d94dfcd:6dfdca88-67d6-48e4-b6f4-60bb9094221c"
        print(f"[UYARI] account_ids create_checkout yanıtında bulunamadı, fallback kullanılıyor: {account_ids}")

    payment_methods_response, payment_methods_status = await get_payment_methods(checkout_id, auth_token, account_ids)
    if payment_methods_status != 200:
        print(f"[HATA] Ödeme yöntemleri alma başarısız, durum: {payment_methods_status}")
        return payment_methods_response, payment_methods_status

    update_billing_response, update_billing_status = await update_checkout_billing(checkout_id, auth_token)
    if update_billing_status != 200:
        print(f"[HATA] Fatura bilgileri güncelleme başarısız, durum: {update_billing_status}")
        return update_billing_response, update_billing_status

    buyer_id = create_checkout_response.get('buyerInfo', {}).get('visitorId') or str(uuid.uuid4())
    payment_details_response, payment_details_status = await submit_payment_details(checkout_id, auth_token, buyer_id)
    if payment_details_status != 200:
        print(f"[HATA] Ödeme detayları gönderme başarısız, durum: {payment_details_status}")
        return payment_details_response, payment_details_status

    # Ödeme detayları yanıtından detailsId'yi al ve paymentToken olarak kullan
    payment_token = payment_details_response.get('detailsId')
    if not payment_token:
        print(f"[UYARI] detailsId yanıtta bulunamadı, rastgele UUID kullanılıyor")
        payment_token = str(uuid.uuid4())
    else:
        print(f"[BILGI] paymentToken (detailsId) alındı: {payment_token}")

    order_and_charge_response, order_and_charge_status = await create_order_and_charge(checkout_id, auth_token, payment_token)
    if order_and_charge_status != 200:
        print(f"[HATA] Sipariş oluştur ve ödeme başlatma başarısız, durum: {order_and_charge_status}")
        return order_and_charge_response, order_and_charge_status

    # Ödeme tamamlama adımını çağır
    finalize_payment_response, finalize_payment_status = await finalize_payment(checkout_id, auth_token, payment_details_response)
    print(f"[BILGI] Süreç tamamlandı, ödeme tamamlama durumu: {finalize_payment_status}")
    return finalize_payment_response, finalize_payment_status

if __name__ == '__main__':
    asyncio.run(full_process())