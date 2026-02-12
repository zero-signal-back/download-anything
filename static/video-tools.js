// Video Tools - Automatic Server/Client Fallback
// If server fails or file > 50MB, automatically use browser processing

const MAX_SERVER_SIZE = 50 * 1024 * 1024; // 50MB
let ffmpeg = null;
let useClientSide = false;

// Load FFmpeg.wasm for client-side processing
async function loadFFmpeg() {
    if (!ffmpeg && typeof FFmpegWASM !== 'undefined') {
        try {
            const { FFmpeg } = FFmpegWASM;
            ffmpeg = new FFmpeg();
            await ffmpeg.load();
            return true;
        } catch (e) {
            console.error('FFmpeg load failed:', e);
            return false;
        }
    }
    return !!ffmpeg;
}

// Check if should use client-side processing
function shouldUseClientSide(fileSize) {
    return fileSize > MAX_SERVER_SIZE;
}

// Client-side GIF conversion
async function clientGifConvert(file, start, duration, fps = 10) {
    if (!await loadFFmpeg()) throw new Error('FFmpeg not available');
    
    const inputName = 'input.mp4';
    const outputName = 'output.gif';
    
    const fileData = await file.arrayBuffer();
    await ffmpeg.writeFile(inputName, new Uint8Array(fileData));
    
    await ffmpeg.exec([
        '-i', inputName,
        '-ss', String(start),
        '-t', String(duration),
        '-vf', `fps=${fps},scale=320:-1`,
        outputName
    ]);
    
    const data = await ffmpeg.readFile(outputName);
    return new Blob([data.buffer], { type: 'image/gif' });
}

// Client-side video compression
async function clientCompress(file, quality = 'medium') {
    if (!await loadFFmpeg()) throw new Error('FFmpeg not available');
    
    const inputName = 'input.mp4';
    const outputName = 'compressed.mp4';
    const crfValues = { high: '23', medium: '28', low: '35' };
    const crf = crfValues[quality] || '28';
    
    const fileData = await file.arrayBuffer();
    await ffmpeg.writeFile(inputName, new Uint8Array(fileData));
    
    await ffmpeg.exec([
        '-i', inputName,
        '-vcodec', 'libx264',
        '-crf', crf,
        '-preset', 'ultrafast',
        outputName
    ]);
    
    const data = await ffmpeg.readFile(outputName);
    return new Blob([data.buffer], { type: 'video/mp4' });
}

// Client-side video rotation
async function clientRotate(file, rotation) {
    if (!await loadFFmpeg()) throw new Error('FFmpeg not available');
    
    const inputName = 'input.mp4';
    const outputName = 'rotated.mp4';
    
    const transposeMap = {
        '90': '1',
        '180': '2,transpose=2',
        '270': '2'
    };
    const transpose = transposeMap[rotation] || '1';
    
    const fileData = await file.arrayBuffer();
    await ffmpeg.writeFile(inputName, new Uint8Array(fileData));
    
    await ffmpeg.exec([
        '-i', inputName,
        '-vf', `transpose=${transpose}`,
        '-c:a', 'copy',
        outputName
    ]);
    
    const data = await ffmpeg.readFile(outputName);
    return new Blob([data.buffer], { type: 'video/mp4' });
}

// Client-side format conversion
async function clientConvert(file, format) {
    if (!await loadFFmpeg()) throw new Error('FFmpeg not available');
    
    const inputName = 'input.mp4';
    const outputName = `output.${format}`;
    
    const fileData = await file.arrayBuffer();
    await ffmpeg.writeFile(inputName, new Uint8Array(fileData));
    
    await ffmpeg.exec([
        '-i', inputName,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        outputName
    ]);
    
    const data = await ffmpeg.readFile(outputName);
    return new Blob([data.buffer], { type: `video/${format}` });
}

// Universal process function with automatic fallback
async function processVideoUniversal(file, toolType, options, statusCallback) {
    const fileSize = file.size;
    useClientSide = shouldUseClientSide(fileSize);
    
    if (useClientSide) {
        statusCallback('info', `File size: ${(fileSize/1024/1024).toFixed(1)}MB - Using browser processing`);
    }
    
    try {
        // Try server-side first if file is small
        if (!useClientSide) {
            statusCallback('processing', 'Uploading to server...');
            const result = await serverProcess(file, toolType, options, statusCallback);
            return result;
        }
    } catch (serverError) {
        console.log('Server failed, falling back to client-side:', serverError);
        statusCallback('info', 'Server busy - switching to browser processing...');
        useClientSide = true;
    }
    
    // Client-side processing
    if (useClientSide) {
        statusCallback('processing', 'Processing in browser...');
        
        let blob;
        if (toolType === 'gif') {
            blob = await clientGifConvert(file, options.start, options.duration, options.fps);
        } else if (toolType === 'compress') {
            blob = await clientCompress(file, options.quality);
        } else if (toolType === 'rotate') {
            blob = await clientRotate(file, options.rotation);
        } else if (toolType === 'convert') {
            blob = await clientConvert(file, options.format);
        }
        
        return { blob, filename: `output_${Date.now()}.${toolType === 'gif' ? 'gif' : 'mp4'}` };
    }
}

// Server-side processing
async function serverProcess(file, toolType, options, statusCallback) {
    const formData = new FormData();
    formData.append('video', file);
    
    // Add tool-specific parameters
    Object.keys(options).forEach(key => {
        formData.append(key, options[key]);
    });
    
    const endpoints = {
        'gif': '/video-to-gif',
        'compress': '/compress-video',
        'rotate': '/rotate-video',
        'convert': '/convert-format',
        'watermark': '/remove-watermark'
    };
    
    const response = await fetch(endpoints[toolType], {
        method: 'POST',
        body: formData
    });
    
    const data = await response.json();
    
    if (!data.success) {
        throw new Error(data.error || 'Server processing failed');
    }
    
    return { filename: data.filename, serverFile: true };
}

// Download helper
function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}
