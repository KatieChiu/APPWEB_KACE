from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import os
import urllib.parse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid

load_dotenv()

app = FastAPI()

os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

def send_email(subject: str, body_text: str, body_html: str = None) -> bool:
    sender = os.getenv("SMTP_SENDER")
    password = os.getenv("SMTP_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    recipient = os.getenv("EMAIL_TO")
    
    if not all([sender, password, smtp_server, recipient]):
        print("Faltan variables SMTP en .env")
        return False
    
    msg = MIMEMultipart("alternative")
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
  
    msg.attach(MIMEText(body_text, "plain", "utf-8"))
    
    
    if body_html:
        msg.attach(MIMEText(body_html, "html", "utf-8"))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())
        server.quit()
        print(f"Correo enviado correctamente a: {recipient}")
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.post("/generar", response_class=HTMLResponse)
async def generar(
    email: str = Form(...),
    prompt: str = Form(...)
):
    safe_prompt = prompt.replace("'", "\\'").replace('"', '\\"').replace("\n", " ")
    encoded_prompt = urllib.parse.quote(prompt)
   
    api_key = os.getenv("key_API")
    if not api_key:
        return HTMLResponse(content="<p class='text-red-400 text-center text-xl'>Error: API key no configurada en .env (key_API)</p>")

    img_html = ""
    for i in range(4):
        seed = 2000 + i
        url = f"https://gen.pollinations.ai/image/{encoded_prompt}?model=flux&seed={seed}&width=1024&height=1024&key={api_key}"
       
        img_html += (
            f"<div class='bg-gray-800 rounded-2xl overflow-hidden shadow-xl border border-white/5 relative'>"
            f"<img src='{url}' loading='lazy' "
            f"class='w-full cursor-pointer hover:scale-105 transition duration-500' "
            f"onerror=\"this.src='https://placehold.co/1024x1024/ff4444/fff/png?text=Error'; this.nextSibling.style.display='flex';\" "
            f"onclick=\"elegir('{url.replace("'", "\\'")}', '{safe_prompt}', '{email.replace("'", "\\'")}')\">"
            f"<div class='absolute inset-0 flex items-center justify-center bg-gray-900/70 hidden text-white text-center p-6'>"
            f"  <div>"
            f"    <svg class='animate-spin h-12 w-12 mx-auto mb-4 text-cyan-400' xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24'>"
            f"      <circle class='opacity-25' cx='12' cy='12' r='10' stroke='currentColor' stroke-width='4'></circle>"
            f"      <path class='opacity-75' fill='currentColor' d='M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z'></path>"
            f"    </svg>"
            f"    <p class='text-lg font-bold'>Generando diseño {i+1}...</p>"
            f"    <p class='text-sm mt-2'>Puede tardar 5-20 segundos.</p>"
            f"  </div>"
            f"</div>"
            f"</div>"
        )

    content = f"""
    <div class="text-center animate-in fade-in duration-700">
        <h2 class="text-3xl font-bold mb-4 text-white">Elige tu diseño favorito</h2>
        <p class="text-slate-400 mb-8">Correo del cliente: {email}</p>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
            {img_html}
        </div>
        <p class="mt-10 text-slate-500 text-sm">
            Selecciona el diseño que más te guste para continuar con el pedido
        </p>
    </div>
   
    <div id="form-container" class="mt-12"></div>

    <script>
    function elegir(url, p, email) {{
        const target = document.getElementById('form-container');
        target.innerHTML = `
        <div class='bg-white/10 backdrop-blur-xl p-8 rounded-3xl border border-white/20 max-w-lg mx-auto shadow-2xl animate-in slide-in-from-bottom duration-500'>
            <h3 class='text-2xl font-bold mb-6 text-center text-white'>Detalles del Pedido</h3>
            <form hx-post='/carrito' hx-target='#resultado' class='space-y-5'>
                <input type='hidden' name='imagen' value='" + url + "'>
                <input type='hidden' name='prompt' value='" + p + "'>
                <input type='hidden' name='email' value='" + email + "'>
               
                <div>
                    <label class='text-xs text-slate-400 ml-2 block mb-1'>Nombre completo</label>
                    <input type='text' name='nombre' placeholder='Tu nombre' required class='w-full p-4 rounded-xl bg-black/40 text-white border border-white/10 focus:border-cyan-500 outline-none'>
                </div>
               
                <div>
                    <label class='text-xs text-slate-400 ml-2 block mb-1'>Teléfono / WhatsApp</label>
                    <input type='tel' name='telefono' placeholder='+504 9999-9999' required class='w-full p-4 rounded-xl bg-black/40 text-white border border-white/10 focus:border-cyan-500 outline-none'>
                </div>
                <div>
                    <label class='text-xs text-slate-400 ml-2 block mb-1'>Dirección exacta</label>
                    <textarea name='direccion' placeholder='Barrio, calle, casa, referencias...' required class='w-full p-4 rounded-xl bg-black/40 text-white border border-white/10 focus:border-cyan-500 outline-none h-28'></textarea>
                </div>
                <div>
                    <label class='text-xs text-slate-400 ml-2 block mb-1'>Material de impresión</label>
                    <div class="grid grid-cols-2 gap-4 mt-2">
                        <label class="flex flex-col items-center p-4 rounded-xl bg-black/40 border-2 border-transparent has-[:checked]:border-cyan-500 cursor-pointer transition-all">
                            <input type="radio" name="material" value="sublimacion" required class="peer hidden">
                            <span class="font-medium text-white">Sublimación</span>
                            <span class="text-sm text-cyan-400">L 240 c/u</span>
                        </label>
                        <label class="flex flex-col items-center p-4 rounded-xl bg-black/40 border-2 border-transparent has-[:checked]:border-cyan-500 cursor-pointer transition-all">
                            <input type="radio" name="material" value="dtf" class="peer hidden">
                            <span class="font-medium text-white">DTF</span>
                            <span class="text-sm text-cyan-400">L 350 c/u</span>
                        </label>
                    </div>
                </div>
                <div>
                    <label class='text-xs text-slate-400 ml-2 block mb-1'>Cantidad de totes</label>
                    <input type='number' name='cantidad' value='1' min='1' required class='w-full p-4 rounded-xl bg-black/40 text-white border border-white/10 focus:border-cyan-500 outline-none'>
                </div>
                <button type='submit' class='w-full bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold py-4 rounded-2xl transition transform hover:scale-[1.02] active:scale-95 shadow-lg mt-6'>
                    Ver carrito y pagar
                </button>
            </form>
        </div>`;
       
        htmx.process(target);
       
        setTimeout(() => {{
            target.scrollIntoView({{behavior: 'smooth', block: 'center'}});
        }}, 200);
    }}
    </script>
    """
    return HTMLResponse(content=content)


@app.post("/carrito", response_class=HTMLResponse)
async def mostrar_carrito(
    nombre: str = Form(...),
    telefono: str = Form(...),
    direccion: str = Form(...),
    cantidad: int = Form(...),
    material: str = Form(...),
    imagen: str = Form(...),
    prompt: str = Form(...),
    email: str = Form(...)
):
    precios = {"sublimacion": 240, "dtf": 350}
    precio_unitario = precios.get(material, 0)
    material_nombre = "Sublimación" if material == "sublimacion" else "DTF" if material == "dtf" else "No seleccionado"

    subtotal = cantidad * precio_unitario
    descuento = subtotal * 0.20 if cantidad >= 12 else 0
    total = subtotal - descuento

    ticket = f"KACE-{uuid.uuid4().hex[:8].upper()}"

    html = f"""
    <div class='text-center py-12 animate-in fade-in duration-700 max-w-4xl mx-auto'>
        <h2 class='text-4xl md:text-5xl font-black text-white mb-10'>Tu Carrito de Compra</h2>
        
        <div class='bg-black/50 backdrop-blur-lg p-8 rounded-3xl border border-white/10 mb-12'>
            <div class='grid md:grid-cols-2 gap-10'>
                <div>
                    <img src='{imagen}' class='w-full rounded-2xl shadow-2xl border border-white/10' alt='Diseño elegido'>
                    <p class='mt-4 text-slate-300 italic text-center'>"{prompt}"</p>
                </div>
                <div class='text-left space-y-5 text-lg'>
                    <p><strong>Cliente:</strong> {nombre}</p>
                    <p><strong>Material:</strong> {material_nombre}</p>
                    <p><strong>Precio por tote:</strong> L {precio_unitario:,}</p>
                    <p><strong>Cantidad:</strong> {cantidad} tote(s)</p>
                    <p><strong>Subtotal:</strong> L {subtotal:,.0f}</p>
    """

    if descuento > 0:
        html += f"""
                    <p class='text-orange-400 font-medium'>Descuento 20% (por ≥12 unidades): -L {descuento:,.0f}</p>
        """

    html += f"""
                    <p class='text-3xl font-bold mt-8 pt-6 border-t border-white/20'>
                        Total a pagar: <span class='text-green-400'>L {total:,.0f}</span>
                    </p>
                </div>
            </div>
        </div>

        <div class='bg-white/5 p-8 rounded-3xl border border-white/10 max-w-lg mx-auto mb-12'>
            <h3 class='text-2xl font-bold mb-6 text-white'>Datos de pago (simulación)</h3>
            <div class='space-y-6'>
                <div>
                    <label class='text-sm text-slate-400 block mb-2'>Número de tarjeta</label>
                    <div class='w-full p-4 rounded-xl bg-black/60 text-slate-300 border border-white/10'>4242 4242 4242 4242</div>
                </div>
                <div class='grid grid-cols-2 gap-6'>
                    <div>
                        <label class='text-sm text-slate-400 block mb-2'>Vencimiento</label>
                        <div class='w-full p-4 rounded-xl bg-black/60 text-slate-300 border border-white/10'>12/28</div>
                    </div>
                    <div>
                        <label class='text-sm text-slate-400 block mb-2'>CVC</label>
                        <div class='w-full p-4 rounded-xl bg-black/60 text-slate-300 border border-white/10'>123</div>
                    </div>
                </div>
                <div>
                    <label class='text-sm text-slate-400 block mb-2'>Nombre en la tarjeta</label>
                    <div class='w-full p-4 rounded-xl bg-black/60 text-slate-300 border border-white/10'>{nombre}</div>
                </div>
            </div>
        </div>

        <form hx-post='/confirmar-pago' hx-target='#resultado' class='mt-10'>
            <input type='hidden' name='nombre' value='{nombre}'>
            <input type='hidden' name='telefono' value='{telefono}'>
            <input type='hidden' name='direccion' value='{direccion.replace("'", "&apos;")}'>
            <input type='hidden' name='cantidad' value='{cantidad}'>
            <input type='hidden' name='material' value='{material}'>
            <input type='hidden' name='imagen' value='{imagen}'>
            <input type='hidden' name='prompt' value='{prompt.replace("'", "&apos;")}'>
            <input type='hidden' name='email' value='{email}'>
            <input type='hidden' name='ticket' value='{ticket}'>
            <input type='hidden' name='total' value='{total}'>

            <button type='submit' class='bg-gradient-to-r from-green-600 to-emerald-700 hover:from-green-500 hover:to-emerald-600 text-white font-bold text-xl py-5 px-16 rounded-2xl transition transform hover:scale-105 shadow-2xl'>
                Procesar pago (simulado)
            </button>
        </form>
    </div>
    """

    return HTMLResponse(content=html)


@app.post("/confirmar-pago", response_class=HTMLResponse)
async def confirmar_pago(
    nombre: str = Form(...),
    telefono: str = Form(...),
    direccion: str = Form(...),
    cantidad: int = Form(...),
    material: str = Form(...),
    imagen: str = Form(...),
    prompt: str = Form(...),
    email: str = Form(...),
    ticket: str = Form(...),
    total: float = Form(...)
):
    precios = {"sublimacion": 240, "dtf": 350}
    precio_unitario = precios.get(material, 0)
    material_nombre = "Sublimación" if material == "sublimacion" else "DTF" if material == "dtf" else "—"

   
    body_text = f"""
¡Nuevo pedido de totes recibido!

Cliente: {nombre}
Correo: {email}
Teléfono/WhatsApp: {telefono}
Dirección: {direccion}
Cantidad: {cantidad} totes
Material: {material_nombre}
Precio unitario: L {precio_unitario}
Subtotal: L {cantidad * precio_unitario:,.0f}
Descuento: {'20% (-L ' + str(round((cantidad * precio_unitario * 0.2), 0)) + ')' if cantidad >= 12 else 'Ninguno'}
Total: L {total:,.0f}
Ticket / Referencia: {ticket}
Prompt utilizado: {prompt}
Imagen seleccionada (URL): {imagen}
    """.strip()

    
    body_html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px; background: #f9fafb; }}
            h2 {{ color: #0891b2; margin-bottom: 20px; }}
            strong {{ color: #0e7490; }}
            .highlight {{ background: #ecfeff; padding: 15px; border-radius: 8px; margin: 20px 0; }}
            img {{ max-width: 100%; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin: 15px 0; display: block; }}
            .button {{ background: #0891b2; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; margin: 10px 0; }}
            hr {{ border: 0; border-top: 1px solid #e5e7eb; margin: 30px 0; }}
        </style>
    </head>
    <body>
        <h2>¡Nuevo pedido de totes recibido!</h2>
        
        <div class="highlight">
            <p><strong>Cliente:</strong> {nombre}</p>
            <p><strong>Correo:</strong> {email}</p>
            <p><strong>Teléfono/WhatsApp:</strong> {telefono}</p>
            <p><strong>Dirección:</strong> {direccion}</p>
            <p><strong>Cantidad:</strong> {cantidad} totes</p>
        </div>

        <p><strong>Material:</strong> {material_nombre}</p>
        <p><strong>Precio unitario:</strong> L {precio_unitario:,}</p>
        <p><strong>Subtotal:</strong> L {cantidad * precio_unitario:,.0f}</p>
        {f'<p><strong>Descuento 20%:</strong> -L {round((cantidad * precio_unitario * 0.2), 0):,.0f}</p>' if cantidad >= 12 else ''}
        <p style="font-size: 1.4em; font-weight: bold; color: #059669; margin-top: 20px;">
            Total: L {total:,.0f}
        </p>
        <p><strong>Ticket / Referencia:</strong> {ticket}</p>

        <p style="margin-top: 30px;"><strong>Prompt utilizado:</strong><br>{prompt}</p>

        <p style="margin-top: 30px; font-weight: bold;">Imagen seleccionada:</p>
        <img src="{imagen}" alt="Diseño elegido para el tote">
        <p style="color: #555; font-size: 0.95em; margin-top: 10px;">
            (si no carga arriba, haz clic: <a href="{imagen}" class="button">Ver imagen completa</a>)
        </p>

        <hr>

        <p style="color: #555; text-align: center; font-size: 0.95em;">
            ¡Gracias por tu pedido! Nos pondremos en contacto pronto para coordinar pago y entrega.
        </p>
    </body>
    </html>
    """

    subject = f"Pedido CONFIRMADO - {nombre} - {cantidad} totes - {ticket}"

    success = send_email(subject, body_text, body_html)

    if success:
        mensaje = "Tu pedido ha sido enviado correctamente a nuestro equipo."
    else:
        mensaje = "Pedido registrado, pero hubo un problema al enviar el correo. Contacta directamente por WhatsApp."

    html = f"""
    <div class='text-center py-20 animate-in zoom-in duration-500'>
        <div class='inline-flex items-center justify-center w-24 h-24 bg-green-600 rounded-full mb-8 shadow-[0_0_30px_rgba(34,197,94,0.5)] mx-auto'>
            <svg class='w-14 h-14 text-white' fill='none' stroke='currentColor' viewBox='0 0 24 24' stroke-width='4'>
                <path stroke-linecap='round' stroke-linejoin='round' d='M5 13l4 4L19 7'></path>
            </svg>
        </div>
        <h2 class='text-5xl font-black text-white mb-4'>¡Pago simulado con éxito!</h2>
        <p class='text-2xl text-green-400 mb-6'>Ticket: <strong>{ticket}</strong></p>
        
        <div class='bg-black/40 p-8 rounded-3xl max-w-lg mx-auto border border-green-500/30 mb-10'>
            <p class='text-xl mb-6'>Total pagado: <strong class='text-green-300'>L {total:,.0f}</strong></p>
            <p class='text-lg text-slate-300'>{mensaje}</p>
        </div>
        
        <p class='text-slate-400 text-lg'>Pronto nos pondremos en contacto al {telefono} para coordinar pago real y entrega.</p>
        
        <a href='/' class='inline-block mt-10 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold px-12 py-5 rounded-2xl transition transform hover:scale-105 shadow-xl'>
            Volver al inicio
        </a>
    </div>
    """

    return HTMLResponse(content=html)