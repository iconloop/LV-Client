package iconloop.lab.util;

import org.jose4j.jwe.ContentEncryptionAlgorithmIdentifiers;
import org.jose4j.jwe.JsonWebEncryption;
import org.jose4j.jwe.KeyManagementAlgorithmIdentifiers;
import org.jose4j.lang.JoseException;

import javax.crypto.spec.SecretKeySpec;
import java.io.IOException;
import java.net.URI;
import java.security.Key;

import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.ResponseHandler;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.BasicResponseHandler;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.http.impl.client.DefaultHttpClient;


public class JweClient {
    private final URI serverUri;
    private final Key serverPubKey;

    private JsonWebEncryption getSenderJwe(String payload) {
        JsonWebEncryption senderJwe = new JsonWebEncryption();
        senderJwe.setKey(this.serverPubKey);
        senderJwe.setPayload(payload);
        senderJwe.setAlgorithmHeaderValue(KeyManagementAlgorithmIdentifiers.ECDH_ES);
        senderJwe.setEncryptionMethodHeaderParameter(ContentEncryptionAlgorithmIdentifiers.AES_128_GCM);
        return senderJwe;
    }

    private String sendHttpRequest(String message) throws IOException, InterruptedException {

        HttpClient client = new DefaultHttpClient();
        String response_body = "";
        try{
            HttpPost post = new HttpPost(this.serverUri);
            post.setHeader("Authorization", message);
            ResponseHandler<String> rh = new BasicResponseHandler();
            response_body = client.execute(post, rh).replaceAll("\"", "");
        }catch(Exception e){
            e.printStackTrace();
        }finally{
            client.getConnectionManager().shutdown();
        }

        return response_body;
    }

    public String sendMessage(String payload) throws JoseException, IOException, InterruptedException {
        JsonWebEncryption senderJwe = this.getSenderJwe(payload);
        String compactSerialization = senderJwe.getCompactSerialization();
        Key cek = new SecretKeySpec(senderJwe.getContentEncryptionKey(), "AESWrap");
        String httpResponse = this.sendHttpRequest(compactSerialization);

        JsonWebEncryption receiverJwe = new JsonWebEncryption();
        receiverJwe.setKey(cek);
        receiverJwe.setCompactSerialization(httpResponse);

        return receiverJwe.getPlaintextString();
    }

    public JweClient(String serverUri, Key serverPubKey) {
        this.serverUri = URI.create("http://" + serverUri + "/vault");
        this.serverPubKey = serverPubKey;
    }
}
