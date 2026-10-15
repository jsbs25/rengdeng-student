// 语音识别监听器（macOS 原生 SFSpeechRecognizer，中文连续识别）
// 每识别出一句完整语音，输出一行文本到 stdout
import Foundation
import Speech
import AVFoundation

// 请求权限
let sem = DispatchSemaphore(value: 0)
SFSpeechRecognizer.requestAuthorization { status in
    if status != .authorized {
        FileHandle.standardError.write("NO_PERMISSION\n".data(using: .utf8)!)
        exit(1)
    }
    sem.signal()
}
sem.wait()

AVCaptureDevice.requestAccess(for: .audio) { ok in
    if !ok {
        FileHandle.standardError.write("NO_MIC\n".data(using: .utf8)!)
        exit(1)
    }
}

guard let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "zh-CN")) else {
    FileHandle.standardError.write("NO_RECOGNIZER\n".data(using: .utf8)!)
    exit(1)
}

let audioEngine = AVAudioEngine()
let request = SFSpeechAudioBufferRecognitionRequest()
request.shouldReportPartialResults = false
request.taskHint = .dictation

var started = false
recognizer.recognitionTask(with: request) { result, error in
    if let r = result, r.isFinal {
        let text = r.bestTranscription.formattedString
        if !text.isEmpty {
            print(text, flush: true)
        }
    }
    if let err = error as NSError? {
        // 超时/停止：自动重启（识别器 stop 后重新开始）
        if !started { return }
        started = false
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            restart()
        }
    }
}

func restart() {
    guard !started else { return }
    started = true
    do {
        if audioEngine.isRunning { audioEngine.stop() }
        let node = audioEngine.inputNode
        node.removeTap(onBus: 0)
        let fmt = node.outputFormat(forBus: 0)
        node.installTap(onBus: 0, bufferSize: 2048, format: fmt) { buf, _ in
            request.append(buf)
        }
        try audioEngine.start()
    } catch {
        FileHandle.standardError.write("ENGINE_FAIL\n".data(using: .utf8)!)
    }
}

// 启动
restart()
RunLoop.main.run()
