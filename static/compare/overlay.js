/**
 * I would like to use WebGL here for comparing the two images since
 * the GPU can do this much faster, enabling nicer UI elements and
 * it should also be safer since I don't need to read the image buffer
 * directly in JavaScript.
 */

'use strict'

const vertexShaderSource = `
    attribute vec2 aVertex;
    attribute vec2 aUV;
    varying vec2 vTex;
    void main(void) {
        gl_Position = vec4(aVertex, 0.0, 1.0);
        vTex = aUV;
    }
`
const fragmentShaderSource = `
    precision lowp float;
    varying vec2 vTex;
    uniform sampler2D srcSampler;
    uniform bool uDstExists;
    uniform sampler2D dstSampler;
    uniform mat3 uH;
    uniform float uRatio;
    float logistic_half(float x) {
        return 1.0 / (1.0+exp(-6.0 * (x-0.5)));
    }
    float logistic_quarter(float x) {
        return 1.0 / (1.0+exp(-12.0 * (x-0.25)));
    }
    void main(void) {
        float x = vTex.x;
        float y = vTex.y * -1. + 1.;
        vec2 srcPos = vec2(x, y);
        vec4 src = texture2D(srcSampler, srcPos);
        if (uDstExists) {
            vec2 dstPos = vec2((uH[0][0]*x+uH[0][1]*y+uH[0][2]) / (uH[2][0]*x+uH[2][1]*y+uH[2][2]),
                               (uH[1][0]*x+uH[1][1]*y+uH[1][2]) / (uH[2][0]*x+uH[2][1]*y+uH[2][2]));
            vec4 dst;
            if (dstPos.x < 0. || dstPos.x > 1. || dstPos.y < 0. || dstPos.y > 1.) {
                dst = vec4(0.5);
            } else {
                dst = texture2D(dstSampler, dstPos);
            }
            float ratio_h =  logistic_half(uRatio);
            float ratio_q =  logistic_quarter(uRatio);
            float nratio_q = logistic_quarter(1.0 - uRatio);
            gl_FragColor = vec4(
                ((1.0 - nratio_q) * dst.z) + (nratio_q * src.z),
                (ratio_h * dst.y) + ((1.0 - ratio_h) * src.y),
                (ratio_q * dst.x) + ((1.0 - ratio_q) * src.x),
                1.);
        } else {
            gl_FragColor = src;
        }
    }
`

function initOverlay(gl, canvas, sourceimage, targetimage, homography) {
    const shaderProgram = initShaderProgram(gl, vertexShaderSource, fragmentShaderSource)
    gl.useProgram(shaderProgram)
    gl.viewport(0, 0, canvas.width, canvas.height)
    const vertexBuffer = createStaticBuffer(gl, [-1, 1, -1, -1, 1, -1, 1, 1])
    const uvBuffer = createStaticBuffer(gl, [0, 1, 0, 0, 1, 0, 1, 1])
    // Bind first image to a sampler
    const srcSampler = gl.getUniformLocation(shaderProgram, 'srcSampler')
    gl.uniform1i(srcSampler, 0)
    gl.activeTexture(gl.TEXTURE0)
    bindTexture(gl, sourceimage)
    // bind second image to another sampler
    const dstSampler = gl.getUniformLocation(shaderProgram, 'dstSampler')
    gl.uniform1i(dstSampler, 1)
    const dstExists = gl.getUniformLocation(shaderProgram, 'uDstExists')
    if (targetimage.currentSrc) {
        gl.uniform1i(dstExists, 1)
        gl.activeTexture(gl.TEXTURE1)
        bindTexture(gl, targetimage)
    } else {
        gl.uniform1i(dstExists, 0)
    }
    const uHomography = gl.getUniformLocation(shaderProgram, 'uH')
    homography[2] /= canvas.width
    homography[5] /= canvas.height
    gl.uniformMatrix3fv(uHomography, false, homography)
    // bind all the vertex buffers to their respective attributes
    bindBufferToVertexAttrib(gl, shaderProgram, vertexBuffer, 'aVertex')
    bindBufferToVertexAttrib(gl, shaderProgram, uvBuffer, 'aUV')
    // set color ratio
    const colorRatio = gl.getUniformLocation(shaderProgram, 'uRatio')
    gl.uniform1f(colorRatio, 0.5)
    // draw everything
    gl.drawArrays(gl.TRIANGLE_FAN, 0, 4)
    let doUpdateCanvas = true
    canvas.onmousemove = (mouseEvent) => {
        if (doUpdateCanvas) {
            const mousePosition = getMousePosition(canvas, mouseEvent)
            gl.uniform1f(colorRatio, mousePosition.x)
            gl.drawArrays(gl.TRIANGLE_FAN, 0, 4)
        }
    }
    canvas.onclick = () => {
        if (doUpdateCanvas) {
            doUpdateCanvas = false
            canvas.style['border-style'] = 'dashed'
            canvas.style['border-color'] = 'blue'
        } else {
            doUpdateCanvas = true
            canvas.style['border-style'] = 'solid'
            canvas.style['border-color'] = 'lightgrey'
        }
    }
}

/**
 * Returns the position of the mouse on the canvas.
 * The position is normalized, its always in range [0.0, 1.0].
 */
function getMousePosition(canvas, evt) {
    const rect = canvas.getBoundingClientRect();
    return {
        x: (evt.clientX - rect.left) / canvas.width,
        y: (evt.clientY - rect.top) / canvas.height
    }
}

function bindBufferToVertexAttrib(gl, shaderProgram, buffer, attribName) {
    const attribute = gl.getAttribLocation(shaderProgram, attribName)
    gl.enableVertexAttribArray(attribute)
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer)
    gl.vertexAttribPointer(attribute, 2, gl.FLOAT, false, 0, 0)
}

function createStaticBuffer(gl, bufferDataList) {
    const buffer = gl.createBuffer()
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer)
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(bufferDataList), gl.STATIC_DRAW)
    return buffer
}

function bindTexture(gl, imageElement) {
    const texture = gl.createTexture()
    gl.bindTexture(gl.TEXTURE_2D, texture)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST)
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, imageElement)
}

function initShaderProgram(gl, vsSource, fsSource) {
    const vertexShader = loadShader(gl, gl.VERTEX_SHADER, vsSource)
    const fragmentShader = loadShader(gl, gl.FRAGMENT_SHADER, fsSource)
    const shaderProgram = gl.createProgram()
    gl.attachShader(shaderProgram, vertexShader)
    gl.attachShader(shaderProgram, fragmentShader)
    gl.linkProgram(shaderProgram)
    return shaderProgram
}

function loadShader(gl, type, source) {
    const shader = gl.createShader(type)
    gl.shaderSource(shader, source)
    gl.compileShader(shader)
    return shader
}

function loadImage(imageFilename, targetImgElement) {
    return new Promise((resolve, reject) => {
        targetImgElement.onload = resolve
        targetImgElement.onerror = reject
        targetImgElement.src = staticRoot + "compare/image/" + imageFilename.slice(0, 9) + "/" + imageFilename
    })
}

async function updateImages(pagepairId, sourceimage, sourcelink, targetimage, targetlink) {
    const pagepairResponse = await fetch('/pagepair/' + pagepairId)
    const pagepair = await pagepairResponse.json()
    sourcelink.text = "IIIF: " + pagepair['firstbook'] + "-" + pagepair['firstpage']
    sourcelink.href = "http://codh.rois.ac.jp/iiif/iiif-curation-viewer/index.html?pages=" + pagepair['firstbook'] + "&pos=" + pagepair['firstpage']
    targetlink.text = "IIIF: " + pagepair['secondbook'] + "-" + pagepair['secondpage']
    targetlink.href = "http://codh.rois.ac.jp/iiif/iiif-curation-viewer/index.html?pages=" + pagepair['secondbook'] + "&pos=" + pagepair['secondpage']
    const firstPromise = loadImage(pagepair['first'], sourceimage)
    const secondPromise = loadImage(pagepair['second'], targetimage)
    await Promise.all([firstPromise, secondPromise])
    return pagepair['homography']
}

function updateImagesOnChecked(checkbox, sourceimage, sourcelink, targetimage, targetlink, gl, canvas) {
    if (checkbox.checked) {
        updateImages(checkbox.value, sourceimage, sourcelink, targetimage, targetlink).then((homography) => {
            initOverlay(gl, canvas, sourceimage, targetimage, homography)
        })
    }
}

window.addEventListener('load', () => {
    const canvas = document.getElementById('overlay')
    const gl = canvas.getContext('webgl')
    const sourceimage = document.getElementById('sourceimage')
    const targetimage = document.getElementById('targetimage')
    const sourcelink = document.getElementById('sourcelink')
    const targetlink = document.getElementById('targetlink')
    const radioButtons = Array.from(document.getElementsByName('match'))
    if (!radioButtons.map(button => button.checked).some(x => x === true)) {
        initOverlay(gl, canvas, sourceimage, targetimage, [1, 1, 1, 1, 1, 1, 1, 1, 1])
    }
    radioButtons.forEach(button => {
        updateImagesOnChecked(button, sourceimage, sourcelink, targetimage, targetlink, gl, canvas)
        button.onclick = (event) => {
            updateImagesOnChecked(button, sourceimage, sourcelink, targetimage, targetlink, gl, canvas)
        }
    })
}, false)