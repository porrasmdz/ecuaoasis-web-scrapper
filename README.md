TODO:
1. Registrarse para la API [DONE]
2. Tener credenciales para API Shopify [DONE]

Por cada link en una lista de links:
3. Validar que sea el link valido de un producto [DONE]
3.1 Como se enmascara IP SELECCIONAR ubicacion a País (elegido) [TODO]
4. Ubicar datos de interes del producto [DONE]
5. Adjuntar a matriz de datos para ingresar [DONE]

6. API POST con productos de shopify [DONE]

Por cada producto en la matriz de datos:
7. Registrar producto con su respectiva información, costo y precio de envío [DONE]
8. Confimar que el producto se registró exitosamente [DONE]
9. Actualizar matriz [DONE]

10. Concluir con cuadro de diálogo. Recordar que los precios deben actualizarse manualmente,
si el proveedor cambia (Hasta prox. versión) [TODO]



#IP STRATS, HTTP, PROXIES AND OTHER STRATS
https://www.zenrows.com/blog/selenium-avoid-bot-detection#rotating-http-headers

#TEMPLATES FOR UNDETECTION (DOES NOT HIDE IP, DOES NOT FAKE USER AGENT, DOES NOT REUSE COOKIES, DOES NOT FAKE INTERACTION SMOOTHLY, DOES NOT REMOVE JS META)
https://stackoverflow.com/questions/77907712/how-to-avoid-selenium-detection-or-change-approach
https://pypi.org/project/undetected-chromedriver/
https://github.com/ultrafunkamsterdam/undetected-chromedriver/blob/master/example/example.py