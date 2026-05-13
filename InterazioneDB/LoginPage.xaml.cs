using System.Net.Http.Json;
using System.Text;
using System.Text.Json;

public partial class LoginPage : ContentPage
{
    private readonly HttpClient _client = new() { BaseAddress = new Uri("http://10.0.2.2:5000") };

    private async void OnLoginClicked(object sender, EventArgs e)
    {
        var payload = new { Email = txtEmail.Text, Password = txtPwd.Text };
        var json = JsonSerializer.Serialize(payload);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        try {
            var response = await _client.PostAsync("/api/login", content);
            var result = await response.Content.ReadFromJsonAsync<ApiResponse>();
            lblResult.Text = result?.message ?? "Errore";
            if (result?.success == true) {
                Preferences.Set("Token", result.token);
                lblResult.TextColor = Colors.Green;
            } else { lblResult.TextColor = Colors.Red; }
        } catch (Exception ex) { lblResult.Text = ex.Message; lblResult.TextColor = Colors.Red; }
    }
}

// Helper class per deserializzazione
class ApiResponse { public bool success { get; set; } public string message { get; set; } public string token { get; set; } }