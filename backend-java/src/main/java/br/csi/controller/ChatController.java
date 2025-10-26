package br.csi.controller;

import br.csi.model.ChatRequest;
import br.csi.model.ChatResponse;
import br.csi.service.ChatService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/chat")
public class ChatController {
    private final ChatService chatService;

    public ChatController(ChatService chatService) {
        this.chatService = chatService;
    }

    @PostMapping("/ask")
    public ResponseEntity<ChatResponse> askQuestion(@RequestBody ChatRequest chatRequest) {
        try {
            String answer = chatService.getAnswer(chatRequest.getQuestion());

            ChatResponse chatResponse = new ChatResponse(answer);

            return ResponseEntity.ok(chatResponse);
        } catch (Exception e) {
            e.printStackTrace();

            return ResponseEntity.internalServerError()
                    .body(new ChatResponse("Erro interno ao processar a requisição: " + e.getMessage()));
        }
    }

    @PostMapping("/upload")
    public ResponseEntity<String> uploadFile(
            @RequestParam("file") MultipartFile file,
            @RequestHeader("Authorization")  String authorization
    ) {
        try {
            String message = chatService.uploadFile(file, authorization);
            return ResponseEntity.ok(message);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.internalServerError()
                    .body("Erro interno ao processar a upload: " + e.getMessage());
        }
    }
}
