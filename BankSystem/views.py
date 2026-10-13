from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import login
from django.db import transaction, IntegrityError, DatabaseError
from django.contrib.auth.hashers import make_password,check_password
from django.db.models import F
from django.contrib import messages
from accounts_admin_databaseSide.models import Details,Profile,Reg_Log_information,Balance,Details,RequestaRgWi

def Home(request):
    logged_in = 'user_id' in request.session
    return render(request,'HomePage.html',{
        'logged_in': logged_in
    })

import logging
logger = logging.getLogger(__name__)

# def profile(request):
#     if 'user_id' not in request.session:
#         return redirect('Login')

#     try:
#         user_id = request.session.get('user_id')
#         user = Reg_Log_information.objects.get(id=user_id)

#         registration = user.reg_num

#         if str(registration) == "602610001141000":
#             return redirect('adminpage')

#         # একজন ব্যবহারকারীর Balance record একাধিক হলে প্রথমটি নেবে
#         BalanceData = Balance.objects.filter(
#             reg=registration
#         ).first()

        # if BalanceData is None:
        #     return render(request, "Profile.html", {
        #         'error': 'এই account-এর Balance record পাওয়া যায়নি।',
        #         'activities': Details.objects.filter(
        #             reg=registration
        #         ).order_by('-DaT')
        # })

    #     ProfileData = Profile.objects.filter(
    #         reg_num=registration
    #     ).first()


    #     if request.method == "POST":
    #         amount = request.POST.get('Amount')
    #         type_of = request.POST.get('TypeOf')

    #         if amount and type_of:
    #             RequestaRgWi.objects.create(
    #                 Reg=registration,
    #                 Mobile=ProfileData.mobile,
    #                 TypeOf=type_of,
    #                 Ammount=amount
    #             )

    #             return redirect('profile')

    #     details = Details.objects.filter(
    #         reg=registration
    #     ).order_by('-DaT')

    #     return render(request, "Profile.html", {
    #         'BalanceData': BalanceData,
    #         'ProfileData': ProfileData,
    #         'activities': details
    #     })

    # except Exception:
    #     logger.exception("Error occurred in profile view")
    #     raise


    # details = Details.objects.filter(reg=registration).order_by('-DaT')

    # return render(request, "Profile.html",{'BalanceData' : BalanceData, 'ProfileData' : ProfileData,'activities': details})


def profile(request):
    if 'user_id' not in request.session:
        return redirect('Login')

    user_id = request.session.get('user_id')
    user = Reg_Log_information.objects.get(id=user_id)
    registration = user.reg_num

    if request.method == "POST":
        amount = request.POST.get('Amount')
        type_of = request.POST.get('TypeOf')

        if amount and type_of:
            RequestaRgWi.objects.create(
                Reg=registration,
                Mobile=user.mobile,
                TypeOf=type_of,
                Ammount=amount
            )
            return redirect('profile')

    BalanceData = Balance.objects.filter(
        reg=registration
    ).first()

    ProfileData = Profile.objects.filter(
        reg_num=registration
    ).first()

    details = Details.objects.filter(
        reg=registration
    ).order_by('-DaT')

    print("Registration:", registration)
    print("BalanceData:", BalanceData)
    print("ProfileData:", ProfileData)

    return render(request, "Profile.html", {
        'BalanceData': BalanceData,
        'ProfileData': ProfileData,
        'activities': details
    })


import logging
logger = logging.getLogger(__name__)

def Registration(request):
    if 'user_id' in request.session:
        return redirect('profile')

    if request.method == "POST":
        # Step 1: Form data collect
        try:
            name = request.POST.get('Name', '').strip()
            username = request.POST.get('UserName', '').strip()
            batch = request.POST.get('Batch', '').strip()
            reg_input = request.POST.get('Registration', '').strip()
            mobile_input = request.POST.get('Mobile', '').strip()
            password = request.POST.get('Password', '')

            # Step 2: Empty field check
            if not all([
                name, username, batch,
                reg_input, mobile_input, password
            ]):
                return render(request, "Registration.html", {
                    'error': 'Shob field puron korun.'
                })

            # Step 3: Number validation
            try:
                reg_num = reg_input
                mobile = mobile_input
            except ValueError:
                return render(request, "Registration.html", {
                    'error': 'Registration number ebong mobile-e valid number din.'
                })

            if int(reg_num) <= 0 or int(mobile) <= 0:
                return render(request, "Registration.html", {
                    'error': 'Registration ebong mobile number valid hote hobe.'
                })

            # Step 4: Duplicate registration check
            if Reg_Log_information.objects.filter(
                reg_num=reg_num
            ).exists():
                return render(request, "Registration.html", {
                    'error': 'Ei registration number diye account ache.'
                })

            # Step 5: Duplicate username check
            if Reg_Log_information.objects.filter(
                UserName=username
            ).exists():
                return render(request, "Registration.html", {
                    'error': 'Ei username age thekei newa hoyeche.'
                })

            # Step 6: Create account and profile together
            hash_pass = make_password(password)

            with transaction.atomic():
                Reg_Log_information.objects.create(
                    name=name,
                    UserName=username,
                    mobile=mobile,
                    reg_num=reg_num,
                    batch=batch,
                    password=hash_pass
                )

                Profile.objects.create(
                    naem=name,
                    UserName=username,
                    mobile=mobile,
                    reg_num=reg_num,
                    batch=batch
                )

            logger.info(
                "Registration successful. Registration number: %s",
                reg_num
            )

            return redirect('Login')

        except IntegrityError:
            logger.exception(
                "Registration failed at database constraint check."
            )
            return render(request, "Registration.html", {
                'error': 'Ei data diye account create kora jayni. '
                         'Registration number ba username check korun.'
            })

        except DatabaseError:
            logger.exception(
                "Registration failed due to database error."
            )
            return render(request, "Registration.html", {
                'error': 'Database-e somossa hoyeche. '
                         'Pore abar chesta korun.'
            })

        except Exception:
            logger.exception(
                "Unexpected error occurred in Registration view."
            )
            return render(request, "Registration.html", {
                'error': 'Registration-e unexpected somossa hoyeche. '
                         'Admin-ke log check korte bolun.'
            })

    return render(request, "Registration.html")

def Login(request):
    if 'user_id' in request.session:
        return redirect('profile')
    if request.method == "POST":
        UserName = request.POST.get('username')
        Registration = request.POST.get('registration')
        password = request.POST.get('password')
        user = Reg_Log_information.objects.get(reg_num = Registration,UserName = UserName)

        if check_password(password, user.password):
            request.session['user_id'] = user.id
            return redirect('profile')
        else:
            return redirect('Home')
    return render(request, 'Login.html')

def LogOut(request):
    request.session.flush()
    return redirect('Login')

logger = logging.getLogger(__name__)


def Admin(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('Login')

    try:
        user = Reg_Log_information.objects.get(id=user_id)

        # Admin registration number
        ADMIN_REG = "0602610001141000"

        if str(user.reg_num).strip() != ADMIN_REG:
            return redirect('profile')

        if request.method == "POST":
            action = request.POST.get('action')

            # ==================================
            # 1. DEPOSIT
            # ==================================
            if action == 'add':
                DepDetReg = request.POST.get('DRegistration')
                AmDep = request.POST.get('AmDep')
                depReson = request.POST.get('depReson')

                if not DepDetReg or not AmDep or not depReson:
                    messages.error(
                        request,
                        "Please fill in all deposit fields."
                    )
                    return redirect('adminpage')

                try:
                    AmDep = int(AmDep)
                except (ValueError, TypeError):
                    messages.error(request, "Invalid deposit amount.")
                    return redirect('adminpage')

                if AmDep <= 0:
                    messages.error(
                        request,
                        "Deposit amount must be greater than zero."
                    )
                    return redirect('adminpage')

                with transaction.atomic():
                    # Update only the selected user's balance
                    balance = Balance.objects.select_for_update().get(
                        reg=DepDetReg
                    )

                    balance.AvBalance += AmDep
                    balance.ConsBalance += AmDep
                    balance.save()

                    Details.objects.create(
                        reg=DepDetReg,
                        reason=depReson
                    )

                messages.success(request, "Deposit successful.")

            # ==================================
            # 2. RECHARGE REQUEST CONFIRM
            # ==================================
            elif action == 'confirm':
                request_id = request.POST.get('request_id')

                if not request_id:
                    messages.error(
                        request,
                        "Recharge request ID is missing."
                    )
                    return redirect('adminpage')

                with transaction.atomic():
                    recharge = RequestaRgWi.objects.select_for_update().get(
                        id=request_id
                    )

                    balance = Balance.objects.select_for_update().get(
                        reg=recharge.Reg
                    )

                    amount = recharge.Ammount

                    if amount <= 0:
                        messages.error(
                            request,
                            "Invalid recharge amount."
                        )
                    elif balance.AvBalance < amount:
                        messages.error(
                            request,
                            "Insufficient available balance."
                        )
                    else:
                        balance.AvBalance -= amount
                        balance.save(update_fields=['AvBalance'])

                        recharge.delete()

                        messages.success(
                            request,
                            "Recharge request confirmed."
                        )

            # ==================================
            # 3. RECHARGE REQUEST DELETE
            # ==================================
            elif action == 'delete':
                request_id = request.POST.get('request_id')

                if request_id:
                    deleted, _ = RequestaRgWi.objects.filter(
                        id=request_id
                    ).delete()

                    if deleted:
                        messages.success(
                            request,
                            "Recharge request deleted."
                        )
                    else:
                        messages.error(
                            request,
                            "Recharge request not found."
                        )
                else:
                    messages.error(
                        request,
                        "Recharge request ID is missing."
                    )

            else:
                messages.error(request, "Invalid action.")

            return redirect('adminpage')

        # ==================================
        # GET: SHOW ADMIN PAGE
        # ==================================
        WithdrawData = RequestaRgWi.objects.all().order_by('id')
        data = Balance.objects.all()

        return render(request, 'Admin.html', {
            'data': data,
            'WithdrawData': WithdrawData
        })

    except (
        Reg_Log_information.DoesNotExist,
        Balance.DoesNotExist,
        RequestaRgWi.DoesNotExist,
    ):
        logger.exception("Required database record not found in Admin view")
        return render(request, 'Admin.html', {
            'data': Balance.objects.none(),
            'WithdrawData': RequestaRgWi.objects.none(),
            'error': 'Required account or balance record was not found.'
        })

    except Exception:
        logger.exception("Unexpected error in Admin view")
        raise
