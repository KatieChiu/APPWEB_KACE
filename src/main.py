from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import os
import urllib.parse

load_dotenv()

app = FastAPI()

os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)


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
        return HTMLResponse(content="<p class='text-red-400 text-center text-xl'>Error: API key no configurada en .env</p>")

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
            <form hx-post='/enviar' hx-target='#resultado' class='space-y-5'>
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
                    <label class='text-xs text-slate-400 ml-2 block mb-1'>Cantidad de totes</label>
                    <input type='number' name='cantidad' value='1' min='1' required class='w-full p-4 rounded-xl bg-black/40 text-white border border-white/10 focus:border-cyan-500 outline-none'>
                </div>

                <button type='submit' class='w-full bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold py-4 rounded-2xl transition transform hover:scale-[1.02] active:scale-95 shadow-lg'>
                    Enviar Pedido
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


@app.post("/enviar", response_class=HTMLResponse)
async def enviar(
    nombre: str = Form(...), 
    telefono: str = Form(...), 
    direccion: str = Form(...), 
    cantidad: int = Form(...),
    imagen: str = Form(...),
    prompt: str = Form(...),
    email: str = Form(...)
):

    return f"""
    <div class='text-center py-20 animate-in zoom-in duration-500'>
        <div class='inline-flex items-center justify-center w-20 h-20 bg-cyan-600 rounded-full mb-6 shadow-[0_0_20px_rgba(34,211,238,0.4)] mx-auto'>
            <svg class='w-12 h-12 text-white' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                <path stroke-linecap='round' stroke-linejoin='round' stroke-width='4' d='M5 13l4 4L19 7'></path>
            </svg>
        </div>
        <h2 class='text-4xl font-bold text-white mb-4'>¡Pedido recibido!</h2>
        <p class='text-xl text-cyan-300 mb-8'>Solicitud de {cantidad} tote(s) enviada correctamente</p>
        
        <div class='mt-8 text-slate-300 space-y-4 max-w-md mx-auto'>
            <p class='text-lg'>Gracias, <strong>{nombre}</strong></p>
            <p class='text-sm'>Pronto nos pondremos en contacto contigo para coordinar el pago y la entrega.</p>
            <p class='text-sm text-slate-400 mt-10'>
                Puedes cerrar esta ventana. Gracias por tu pedido.
            </p>
        </div>
    </div>
    """