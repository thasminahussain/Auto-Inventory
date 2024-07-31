from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    View, 
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import (
    PurchaseBill, 
    Supplier, 
    PurchaseItem,
    PurchaseBillDetails,
    SaleBill,  
    SaleItem,
    SaleBillDetails
)
from .forms import (
    SelectSupplierForm, 
    PurchaseItemFormset,
    PurchaseDetailsForm, 
    SupplierForm, 
    SaleForm,
    SaleItemFormset,
    SaleDetailsForm
)
from inventory.models import Stock

# shows a lists of all suppliers
class SupplierListView(ListView):
    model = Supplier
    template_name = "suppliers/suppliers_list.html"
    queryset = Supplier.objects.filter(is_deleted=False)
    paginate_by = 10

# used to add a new supplier
class SupplierCreateView(SuccessMessageMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    success_url = '/transactions/suppliers'
    success_message = "Supplier has been created successfully"
    template_name = "suppliers/edit_supplier.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'New Supplier'
        context["savebtn"] = 'Add Supplier'
        return context     

# used to update a supplier's info
class SupplierUpdateView(SuccessMessageMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    success_url = '/transactions/suppliers'
    success_message = "Supplier details has been updated successfully"
    template_name = "suppliers/edit_supplier.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit Supplier'
        context["savebtn"] = 'Save Changes'
        context["delbtn"] = 'Delete Supplier'
        return context

# used to delete a supplier
class SupplierDeleteView(View):
    template_name = "suppliers/delete_supplier.html"
    success_message = "Supplier has been deleted successfully"

    def get(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        return render(request, self.template_name, {'object' : supplier})

    def post(self, request, pk):  
        supplier = get_object_or_404(Supplier, pk=pk)
        supplier.is_deleted = True
        supplier.save()                                               
        messages.success(request, self.success_message)
        return redirect('suppliers-list')

# used to view a supplier's profile
class SupplierView(View):
    def get(self, request, name):
        supplierobj = get_object_or_404(Supplier, name=name)
        bill_list = PurchaseBill.objects.filter(supplier=supplierobj)
        page = request.GET.get('page', 1)
        paginator = Paginator(bill_list, 10)
        try:
            bills = paginator.page(page)
        except PageNotAnInteger:
            bills = paginator.page(1)
        except EmptyPage:
            bills = paginator.page(paginator.num_pages)
        context = {
            'supplier'  : supplierobj,
            'bills'     : bills
        }
        return render(request, 'suppliers/supplier.html', context)

# shows the list of bills of all purchases 
class PurchaseView(ListView):
    model = PurchaseBill
    template_name = "purchases/purchases_list.html"
    context_object_name = 'bills'
    ordering = ['-time']
    paginate_by = 10

# used to select the supplier
class SelectSupplierView(View):
    form_class = SelectSupplierForm
    template_name = 'purchases/select_supplier.html'

    def get(self, request, *args, **kwargs):                                    # loads the form page
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):                                   # gets selected supplier and redirects to 'PurchaseCreateView' class
        form = self.form_class(request.POST)
        if form.is_valid():
            supplierid = request.POST.get("supplier")
            supplier = get_object_or_404(Supplier, id=supplierid)
            return redirect('new-purchase', supplier.pk)
        return render(request, self.template_name, {'form': form})

# used to generate a bill object and save items
class PurchaseCreateView(View):
    template_name = 'purchases/new_purchase.html'

    def get(self, request, pk):
        formset = PurchaseItemFormset(request.GET or None)  
        supplierobj = get_object_or_404(Supplier, pk=pk) 
        context = {
            'formset': formset,
            'supplier': supplierobj,
        } 
        return render(request, self.template_name, context)

    def post(self, request, pk):
        formset = PurchaseItemFormset(request.POST)  # Receive a post method for the formset
        supplierobj = get_object_or_404(Supplier, pk=pk)  # Get the supplier object
        
        if formset.is_valid():
            try:
                # Create and save the bill object
                billobj = PurchaseBill(supplier=supplierobj)  # Create a PurchaseBill object with the supplier
                billobj.save()  # Save the PurchaseBill object

                # Create and save the bill details object
                billdetailsobj = PurchaseBillDetails(billno=billobj)  # Create PurchaseBillDetails object with the bill
                billdetailsobj.save()  # Save the PurchaseBillDetails object

                # Process each form in the formset
                for form in formset:
                    if form.cleaned_data:  # Ensure form data is valid
                        billitem = form.save(commit=False)  # Save the form without committing to the database yet
                        billitem.billno = billobj  # Link the bill to the item
                        stock = get_object_or_404(Stock, name=billitem.stock.name)  # Get the stock item
                        billitem.totalprice = billitem.perprice * billitem.quantity  # Calculate the total price
                        stock.quantity += billitem.quantity  # Update the stock quantity
                        billdetailsobj.total += billitem.totalprice  # Update the total in bill details
                        stock.save()  # Save the updated stock
                        billitem.save()  # Save the bill item

                billdetailsobj.save()  # Save the updated bill details
                messages.success(request, "Purchased items have been registered successfully")

                return redirect('purchase-bill', billno=billobj.billno)  # Redirect to the purchase bill view

            except Exception as exc:
                print('Exception error! ', exc)
                if 'billobj' in locals():  # Check if billobj exists
                    billobj.delete()  # Clean up if something goes wrong
                context = {
                    'formset': formset,
                    'supplier': supplierobj,
                }
                return render(request, self.template_name, context)

        # If formset is not valid
        context = {
            'formset': formset,
            'supplier': supplierobj,
        }
        return render(request, self.template_name, context)

# used to delete a bill object
class PurchaseDeleteView(SuccessMessageMixin, DeleteView):
    model = PurchaseBill
    template_name = "purchases/delete_purchase.html"
    success_url = '/transactions/purchases'
    
    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        items = PurchaseItem.objects.filter(billno=self.object.billno)
        for item in items:
            stock = get_object_or_404(Stock, name=item.stock.name)
            if stock.is_deleted == False:
                stock.quantity -= item.quantity
                stock.save()
        messages.success(self.request, "Purchase bill has been deleted successfully")
        return super(PurchaseDeleteView, self).delete(*args, **kwargs)

# shows the list of bills of all sales 
class SaleView(ListView):
    model = SaleBill
    template_name = "sales/sales_list.html"
    context_object_name = 'bills'
    ordering = ['-time']
    paginate_by = 10

# # used to generate a bill object and save items
class SaleCreateView(View):                                                      
    template_name = 'sales/new_sale.html'
    
    SALES_TAX_RATE = 0.06

    def get(self, request):
        form = SaleForm(request.GET or None)
        formset = SaleItemFormset(request.GET or None)
        stocks = Stock.objects.filter(is_deleted=False)
        context = {
            'form': form,
            'formset': formset,
            'stocks': stocks
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = SaleForm(request.POST)
        formset = SaleItemFormset(request.POST)
        
        if form.is_valid() and formset.is_valid():
            try:
                billobj = form.save(commit=False)
                billobj.save()

                # Create bill details object
                billdetailsobj = SaleBillDetails(billno=billobj)
                billdetailsobj.save()

                total_price = 0
                for form in formset:
                    billitem = form.save(commit=False)
                    billitem.billno = billobj
                    stock = get_object_or_404(Stock, name=billitem.stock.name)
                    billitem.totalprice = billitem.perprice * billitem.quantity
                    total_price += billitem.totalprice
                    stock.quantity -= billitem.quantity
                    stock.save()
                    billitem.save()

                # Calculate sales tax and update the total
                sales_tax = total_price * self.SALES_TAX_RATE
                subtotal = total_price
                total = subtotal + sales_tax
                
                billdetailsobj.subtotal = subtotal
                billdetailsobj.sales_tax = sales_tax
                billdetailsobj.total = total
                billdetailsobj.save()

                messages.success(request, "Sold items have been registered successfully")
                return redirect('sale-bill', billno=billobj.billno)

            except Exception as exc:
                print('Exception error! ', exc)
                if 'billobj' in locals():
                    billobj.delete()  # Clean up if something goes wrong
                context = {
                    'form': form,
                    'formset': formset,
                }
                return render(request, self.template_name, context)
        
        context = {
            'form': form,
            'formset': formset,
        }
        return render(request, self.template_name, context)


# used to delete a bill object
class SaleDeleteView(SuccessMessageMixin, DeleteView):
    model = SaleBill
    template_name = "sales/delete_sale.html"
    success_url = '/transactions/sales'
    
    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        items = SaleItem.objects.filter(billno=self.object.billno)
        for item in items:
            stock = get_object_or_404(Stock, name=item.stock.name)
            if stock.is_deleted == False:
                stock.quantity += item.quantity
                stock.save()
        messages.success(self.request, "Sale bill has been deleted successfully")
        return super(SaleDeleteView, self).delete(*args, **kwargs)

# # used to display the purchase bill object
class PurchaseBillView(View):
    model = PurchaseBill
    template_name = "bill/purchase_bill.html"
    bill_base = "bill/bill_base.html"

    def get(self, request, billno):
        user = request.user
        context = {
            'bill'          : PurchaseBill.objects.get(billno=billno),
            'items'         : PurchaseItem.objects.filter(billno=billno),
            'billdetails'   : PurchaseBillDetails.objects.get(billno=billno),
            'bill_base'     : self.bill_base,
            'company_name': f"{user.first_name} {user.last_name}",
            'company_email': user.useremail,
        }
        return render(request, self.template_name, context)

    def post(self, request, billno):
        form = PurchaseDetailsForm(request.POST)
        if form.is_valid():
            billdetailsobj = PurchaseBillDetails.objects.get(billno=billno)
            billdetailsobj.total = request.POST.get("total")

            billdetailsobj.save()
            messages.success(request, "Bill details have been modified successfully")
        context = {
            'bill'          : PurchaseBill.objects.get(billno=billno),
            'items'         : PurchaseItem.objects.filter(billno=billno),
            'billdetails'   : PurchaseBillDetails.objects.get(billno=billno),
            'bill_base'     : self.bill_base,
        }
        return render(request, self.template_name, context)


#used to display the sale bill object
class SaleBillView(View):
    model = SaleBill
    template_name = "bill/sale_bill.html"
    bill_base = "bill/bill_base.html"
    
    def get(self, request, billno):
        user = request.user
        bill = get_object_or_404(SaleBill, billno=billno)
        items = SaleItem.objects.filter(billno=billno)
        billdetails = get_object_or_404(SaleBillDetails, billno=billno)
        
        # Calculate subtotal, sales tax, and total if not present
        subtotal = billdetails.subtotal if hasattr(billdetails, 'subtotal') else 0.00
        salestax = billdetails.salestax if hasattr(billdetails, 'salestax') else 0.00
        total = billdetails.total if hasattr(billdetails, 'total') else 0.00

        context = {
            'bill': bill,
            'items': items,
            'billdetails': billdetails,
            'bill_base': self.bill_base,
            'company_name': f"{user.first_name} {user.last_name}",
            'company_email': user.useremail,
            'salesperson': bill.salesperson,
            'payment_method': bill.payment_method,
            'subtotal': subtotal,
            'salestax': salestax,
            'total': total,
        }
        return render(request, self.template_name, context)

    def post(self, request, billno):
        form = SaleDetailsForm(request.POST)
        if form.is_valid():
            billdetailsobj = get_object_or_404(SaleBillDetails, billno=billno)
            billdetailsobj.subtotal = float(request.POST.get("subtotal", 0.00))
            billdetailsobj.salestax = float(request.POST.get("salestax", 0.00))
            billdetailsobj.total = float(request.POST.get("total", 0.00))
            billdetailsobj.save()
        
            messages.success(request, "Bill details have been modified successfully")
    
        return redirect('sale-bill', billno=billno)

