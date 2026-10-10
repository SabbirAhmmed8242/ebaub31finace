from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import login
from django.db import transaction
from django.contrib.auth.hashers import make_password,check_password
from django.db.models import F
from accounts_admin_databaseSide.models import Details,Profile,Reg_Log_information,Balance,Details,RequestaRgWi

def Home(request):
    logged_in = 'user_id' in request.session
    return render(request,'HomePage.html',{
        'logged_in': logged_in
    })

def profile(request):
    if 'user_id' not in request.session:
        return redirect('Login')

    
    user_id = request.session.get('user_id')
    user = Reg_Log_information.objects.get(id = user_id)
    reg = user.reg_num
    print(user)
    if str(user.reg_num) != "6026100001141000":
        registration = user.reg_num
        BalanceData = Balance.objects.get(reg = registration)
        ProfileData = Profile.objects.get(reg_num = registration)
        Mobile = ProfileData.mobile
        if request.method == "POST":
                Ammount = request.POST.get('Amount')
                # Mobile = int(request.POST.get('MobileNo'))
                TypeOf = request.POST.get('TypeOf')
        
                RequestaRgWi.objects.create(
                    Reg = registration,
                    Mobile = Mobile,
                    TypeOf = TypeOf,
                    Ammount = Ammount
                )
    else:
         return redirect('adminpage')

    details = Details.objects.filter(reg=registration).order_by('-DaT')

    return render(request, "Profile.html",{'BalanceData' : BalanceData, 'ProfileData' : ProfileData,'activities': details})

def Registration(request):
    # Already logged in hole profile e pathao
    if 'user_id' in request.session:
        return redirect('profile')

    if request.method == "POST":
        name = request.POST.get('Name', '').strip()
        username = request.POST.get('UserName', '').strip()
        batch = request.POST.get('Batch', '').strip()
        reg_num = int(request.POST.get('Registration', '').strip())
        mobile = int(request.POST.get('Mobile', '').strip())
        password = request.POST.get('Password', '')

        # Kono field faka thakle
        if not all([name, username, batch, reg_num, mobile, password]):
            return render(request, "Registration.html", {
                'error': 'Shob field puron korun.'
            })

        # Reg number ba username age thekei thakle
        if Reg_Log_information.objects.filter(reg_num=reg_num).exists():
            return render(request, "Registration.html", {
                'error': 'Ei registration number diye age thekei account ache.'
            })

        if Reg_Log_information.objects.filter(UserName=username).exists():
            return render(request, "Registration.html", {
                'error': 'Ei username already newa hoyeche.'
            })

        hash_pass = make_password(password)

        # Duita create ek sathe hobe, noyto kono tai hobe na
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

        return redirect('Login')

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

def Admin(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('Login')

    user = Reg_Log_information.objects.get(id=user_id)

    if user.reg_num != 602610001141000:
        return redirect('profile')

    if request.method == "POST":
        action = request.POST.get('action')
        ammount = request.POST.get('ammount')

        DepDetReg = int(request.POST.get('DRegistration'))
        AmDep = int(request.POST.get('AmDep'))
        depReson = request.POST.get('depReson')

        Balance.objects.update(
                        ConsBalance=F('ConsBalance') + int(AmDep)
                        )
        AddMoney = Balance.objects.get(reg = DepDetReg)
        AddMoney.AvBalance += AmDep
        AddMoney.save()
        Details.objects.create(
            reg = DepDetReg,
            reason = depReson
        )


        # 1. Recharge request confirm
        if action == 'confrirm':
            request_id = request.POST.get('request_id')
            Balance.objects.update(
                ConsBalance=F('ConsBalance') - int(ammount)
                )

            with transaction.atomic():
                recharge = RequestaRgWi.objects.get(id=request_id)
                balance = Balance.objects.get(reg=recharge.Reg)

                amount = recharge.Ammount

                if balance.AvBalance < amount:
                    pass
                else:
                    balance.AvBalance -= amount
                    balance.save()
                    recharge.delete()

        # 2. Recharge request delete
        elif action == 'delete':
            request_id = request.POST.get('request_id')
            RequestaRgWi.objects.filter(id=request_id).delete()

        return redirect('adminpage')

    WithdrawData = RequestaRgWi.objects.all()
    data = Balance.objects.get(reg=602610001141000)

    return render(request, 'Admin.html', {
        'data': data,
        'WithdrawData': WithdrawData
    })