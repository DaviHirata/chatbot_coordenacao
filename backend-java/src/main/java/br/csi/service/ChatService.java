package br.csi.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

@Service
public class ChatService {
    private final RestTemplate restTemplate;

    @Value("${rag.api.url}")
    private String RAG_API_URL;

    @Value("${rag.api.upload.url}")
    private String RAG_API_UPLOAD_URL;

    public ChatService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public String getAnswer(String question) {
        try {
            // Corpo da requisição em JSON
            Map<String,String> requestBody = Map.of("prompt", question);

            // Cabeçalhos da requisição
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            // Monta a requisição
            HttpEntity<Map<String, String>> request = new HttpEntity<>(requestBody, headers);

            // Faz a chamada HTTP
            ResponseEntity<Map> response = restTemplate.exchange(
                    RAG_API_URL,
                    HttpMethod.POST,
                    request,
                    Map.class
            );

            // Extrai a resposta
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                return (String)  response.getBody().get("answer");
            } else {
                return "Erro: resposta inválida do serviço Python";
            }
        } catch (RestClientException e) {
            e.printStackTrace();
            return "Erro ao conectar com o serviço Python: " + e.getMessage();
        }
    }

    @Value("${upload.token}")
    private String uploadToken;

    public String uploadFile(MultipartFile file, String authorization) {
        try {
            // Verificar a validade do token
            if (!isValidToken(authorization)) {
                return String.valueOf(ResponseEntity.status(HttpStatus.FORBIDDEN).body("Acesso não autorizado."));
            }

            // Salvar temporariamente o arquivo
            File tempFile = File.createTempFile("upload_", ".pdf");
            file.transferTo(tempFile);

            // Configurar headers
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);

            // Corpo multipart
            MultiValueMap<String, Object> body =  new LinkedMultiValueMap<>();
            body.add("file", new FileSystemResource(tempFile));

            HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);

            ResponseEntity<Map> response = restTemplate.exchange(
                    RAG_API_UPLOAD_URL,
                    HttpMethod.POST,
                    requestEntity,
                    Map.class
            );
            tempFile.delete();

            if (response.getStatusCode().is2xxSuccessful()) {
                return (String)  response.getBody().get("message");
            } else {
                return "Falha ao enviar PDF: resposta inválida da API Python.";
            }
        } catch (IOException e) {
           e.printStackTrace();
           return "Erro ao processar arquivo localmente: " + e.getMessage();
        } catch (Exception e) {
            e.printStackTrace();
            return "Erro ao enviar arquivo para o serviço Python: " + e.getMessage();
        }
    }

    // Método para verificar a validade do token
    private boolean isValidToken(String authorization) {
        // Comparar token enviado com o do .env
        return authorization != null && authorization.equals("Bearer " +  uploadToken);
    }
}
