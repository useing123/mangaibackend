from fastapi import HTTPException
from fastapi.responses import JSONResponse
from mailchimp_transactional import TransactionalEmailsApi, TransactionalEmailsApiException
from mailchimp_transactional.models.send_template_request import SendTemplateRequest
from mailchimp_transactional.models.send_template_response import SendTemplateResponse

mailchimp_api = TransactionalEmailsApi()

class PasswordResetRequest(AppModel):
    email: str

class PasswordResetConfirmation(AppModel):
    token: str
    new_password: str

@router.post("/users/password_reset")
async def request_password_reset(
    password_reset_request: PasswordResetRequest,
    svc: Service = Depends(get_service),
) -> JSONResponse:
    email = password_reset_request.email
    token = svc.repository.generate_password_reset_token(email)

    if token is None:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # MailChimp transactional email sending, make sure to configure the message and template accordingly
        template_name = "password-reset"
        message = {"subject": "Password Reset", "to": [{"email": email}]}
        template_content = [{"name": "TOKEN", "content": token}]
        send_template_request = SendTemplateRequest(key=MAILCHIMP_API_KEY, template_name=template_name, message=message, template_content=template_content)
        response: SendTemplateResponse = mailchimp_api.send_template(send_template_request)

    except TransactionalEmailsApiException as e:
        raise HTTPException(status_code=400, detail=f"Failed to send password reset email: {e}")

    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Password reset email sent."})

@router.post("/users/password_reset_confirm")
async def confirm_password_reset(
    password_reset_confirmation: PasswordResetConfirmation,
    svc: Service = Depends(get_service),
) -> JSONResponse:
    token = password_reset_confirmation.token
    new_password = password_reset_confirmation.new_password

    user = svc.repository.get_user_by_password_reset_token(token)

    if user is None:
        raise HTTPException(status_code=404, detail="Invalid password reset token")

    # Update the password and remove the password reset token
    svc.repository.update_user(
        str(user["_id"]),
        {"password": hash_password(new_password), "password_reset_token": None},
    )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Password reset successfully."})
